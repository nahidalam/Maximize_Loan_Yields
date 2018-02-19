'''
Author: Nahid Alam
'''

import csv
import operator
from loanInterface import facility



#bank_id to facility_id list map
facilityId_by_bankId = {}
#facility_id to facility_obj map
facility_by_facilityId = {}
#list of facility_obj
facilities = []

max_amount_remaining = -1.0
max_amount_remaining_facility_id = 0



def read_facility():
    f = open('large/facilities.csv')
    has_header = csv.Sniffer().has_header(f.read(1024))
    f.seek(0)  # Rewind
    reader = csv.reader(f)
    if has_header:
        next(reader)
    for line in f:
        data_line = line.rstrip().split('\t')
        for item in data_line:
            item_list = item.split(',')
            amount = float(item_list[0])
            interest_rate = float(item_list[1])
            facility_id = item_list[2]
            bank_id = item_list[3]
            facility_obj = facility(amount, interest_rate, facility_id, bank_id)
            facilities.append(facility_obj)
            facility_by_facilityId[item_list[2]] = facility_obj
            if bank_id in facilityId_by_bankId.keys():
                facilityId_by_bankId[bank_id].append(facility_id)
            else:
                facilityId_by_bankId[bank_id] = [facility_id]


def read_covenants():
    f = open('large/covenants.csv')
    has_header = csv.Sniffer().has_header(f.read(1024))
    f.seek(0)  # Rewind
    reader = csv.reader(f)
    if has_header:
        next(reader)
    for line in f:
        data_line = line.rstrip().split('\t')
        for item in data_line:
            item_list = item.split(',')
            bank_id = item_list[2]
            banned_state = item_list[3]
            if item_list[1].isdigit():
                max_default_likelihood = float(item_list[1])
            else:
                max_default_likelihood = -1.0
            if item_list[0] is not None:
                #we have a facility_id so enter its covenants
                facility_id = item_list[0]
                facility_by_facilityId[facility_id].set_max_default_likelihood(max_default_likelihood)
                facility_by_facilityId[facility_id].set_banned_state(banned_state)
            else:
                #have to insert at all the facilities of this bank_id
                for value in facilityId_by_bankId[bank_id]:
                    #each value is a facility_id
                    facility_by_facilityId[value].set_max_default_likelihood(max_default_likelihood)
                    facility_by_facilityId[value].set_banned_state(banned_state)



def grant_loan(item):
    item_list = item.split(',')
    loan_interest_rate = float(item_list[0])
    loan_amount = float(item_list[1])
    loan_id = item_list[2]
    default_likelihood = float(item_list[3])
    banned_state = item_list[4]

    max_expected_yield = -1
    granted_loan_facility_id = None

    loan_yield_facility = []

    for f in facilities:
        if f.get_amount_remaining() >= loan_amount:
            if banned_state != f.get_banned_state() and ((f.get_max_default_likelihood()!=-1.0 and default_likelihood  <= f.get_max_default_likelihood()) or (f.get_max_default_likelihood()==-1.0)):
                #calculate expected_yield
                expected_yield = (1 - default_likelihood) * loan_interest_rate *loan_amount - (default_likelihood * loan_amount) - (f.get_interest_rate() * loan_amount)
                tup = (expected_yield, f.get_facility_id())
                loan_yield_facility.append(tup)

    if len(loan_yield_facility) == 0:
        return
    #we have expected_yield - facility_id list of tupple - sort it based on expected_yield in descending order
    loan_yield_facility.sort(reverse=True)


    '''
    simple heuristics to find which facility_id and max_expected_yield to chose
    We have a system wide max called max_amount_remaining which tracks the max
    remaining amount of loan to grant among all the facilities that follows the
    constraints. While assigning a facility_id to a loan, we always try to keep
    max_amount_remaining as high as possible. That means sometimes not assigning
    the the loan to a facility_id that yields maximum gain. This way we will have
    maximum amount of room to grant any future loan.

    Improvement TODO: Keep system wide max amount of loan per state
    '''
    for item in loan_yield_facility:
        if item[1] == max_amount_remaining_facility_id:
            continue
        else:
            granted_loan_facility_id = item[1]
            max_expected_yield = item[0]

    if granted_loan_facility_id is None:
        yield_facility = loan_yield_facility[0]
        granted_loan_facility_id = yield_facility[1]
        max_expected_yield = yield_facility[0]


    #now we have the facility_id to which we want to grant the loan
    #so find the corresponding object
    facility = facility_by_facilityId[granted_loan_facility_id]

    facility.assign_loan(loan_amount, max_expected_yield,loan_id)

    if granted_loan_facility_id == max_amount_remaining_facility_id:
        max_amount_remaining = -1.0 #reset system max amount loan
        find_max_amount_remaining()


def find_max_amount_remaining():
    global max_amount_remaining
    for f in facilities:
        if f.get_amount_remaining() > max_amount_remaining:
            max_amount_remaining = f.get_amount_remaining()
            max_amount_remaining_facility_id = f.get_facility_id()



def read_loans():
    f = open('large/loans.csv')
    has_header = csv.Sniffer().has_header(f.read(1024))
    f.seek(0)  # Rewind
    reader = csv.reader(f)
    if has_header:
        next(reader)
    for line in f:
        data_line = line.rstrip().split('\t')
        for item in data_line:
            grant_loan(item)

def write_output():
    with open('yields.csv', "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(['facility_id', 'expected_yield'])
        for f in facilities:
            writer.writerow([f.get_facility_id(), f.get_yield_amount()])

    with open('assignments.csv', "w") as new_csv:
        writer = csv.writer(new_csv, delimiter=',')
        writer.writerow(['loan_id', 'facility_id'])
        for f in facilities:
            for l in f.get_loan_ids():
                writer.writerow([l, f.get_facility_id()])





if __name__ == '__main__':
    read_facility()
    read_covenants()
    find_max_amount_remaining()
    read_loans()

    #output to csv
    write_output()
