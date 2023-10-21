from .testData import test_data
from datetime import datetime
import json

mock_details = open('/Users/chaitanya/Downloads/covidform/covid_form/MockStudentData.json')
mock_data = json.load(mock_details)
mock_details.close()


def create_test_data(mongo_instance_caller):
    collection = ''
    final_result_21 = []
    final_result_22 = []
    student_records = []
    collection21 = mongo_instance_caller('formData21')
    collection22 = mongo_instance_caller('formData22')
    student_details = mongo_instance_caller('StudentDetails')
    count = 0
    for record in test_data:
        
        
        if not isinstance(record['affectedDate'], datetime):
            record['affectedDate'] = datetime.strptime(record['affectedDate'], '%Y-%m-%d')
        opposite_collection = ''
        if record['affectedDate'].year == 2021:
            collection = mongo_instance_caller('formData21')
            opposite_collection = mongo_instance_caller('formData22')
        if record['affectedDate'].year == 2022:
            collection = mongo_instance_caller('formData22')
            opposite_collection = mongo_instance_caller('formData21')

        record['symptoms'] = record['symptoms'].split(',')
        
        record['symptoms'] = list(set(record['symptoms']))
        for x in record['symptoms']:
            record['symptoms'].remove(x) if len(x) < 2 else None

        _existing = collection.find_one({'gNumber': record['gNumber']})
        if _existing:
            print('Found duplicate: {dup}'.format(dup=_existing))
            continue
        _opp_existing = opposite_collection.find_one({'gNumber': record['gNumber']})
        if _opp_existing:
            print('Found existing in opp: {dup}'.format(dup=_opp_existing))
            record['name'] = _opp_existing['name']

        print(record['affectedDate'])
        print(record['symptoms'])
        record['country'] = 'USA'
        print(record)
        student = dict(
            gNumber=record['gNumber'],
            email=mock_data[count]['email'],
            phone_number=mock_data[count]['phone_number'],
            state=record['state'],
            country=record['country'],
        )
        print('Student: {s}'.format(s=student))
        student_records.append(student)
        count += 1
        
        if record['affectedDate'].year == 2021:
            final_result_21.append(record)
        if record['affectedDate'].year == 2022:
            final_result_22.append(record)

    collection21.insert_many(final_result_21)
    collection22.insert_many(final_result_22)
    student_details.insert_many(student_records)


def create_duplicate_test_data(mongo_instance_caller):
    count = 0
    final_result_21 = []
    final_result_22 = []
    collection = ''
    collection21 = mongo_instance_caller('formData21')
    collection22 = mongo_instance_caller('formData22')
    for record in test_data:
        print(record)
        if not isinstance(record['affectedDate'], datetime):
            record['affectedDate'] = datetime.strptime(record['affectedDate'], '%Y-%m-%d')
        opposite_collection = ''
        current_date = record['affectedDate']
        current_year = current_date.year
        print(current_date)
        print(current_year)

        if current_year == 2021:
            updated_date = current_date.replace(year=2022)
            collection = mongo_instance_caller('formData22')
            opposite_collection = mongo_instance_caller('formData21')

        print(current_year)

        if current_year == 2022:
            updated_date = current_date.replace(year=2021)
            collection = mongo_instance_caller('formData21')
            opposite_collection = mongo_instance_caller('formData22')

        print(current_year)

        record['affectedDate'] = updated_date

        if not isinstance(record['symptoms'], list):
            record['symptoms'] = record['symptoms'].split(',')
            print(record['symptoms'])
            record['symptoms'] = list(set(record['symptoms']))
            for x in record['symptoms']:
                record['symptoms'].remove(x) if len(x) < 2 else None

        _existing = collection.find_one({'gNumber': record['gNumber']})
        if _existing:
            print('Found duplicate: {dup}, Not saving...'.format(dup=_existing))
            continue
        _opp_existing = opposite_collection.find_one({'gNumber': record['gNumber']})
        if _opp_existing:
            print('Found existing in opposite collection: {dup}'.format(dup=_opp_existing))
            record['name'] = _opp_existing['name']

        if count % 2 == 0:
            if record['hospitalized'] == 'Yes':
                record['hospitalized'] = 'No'
            if record['hospitalized'] == 'No':
                record['hospitalized'] = 'Yes'
        if count % 3 == 0:
            record['hospitalized'] = 'No'
        if count % 5 == 0:
            record['hospitalized'] = 'No'

        if '_id' in record.keys():
            record.pop('_id')

        print(record['affectedDate'])
        record['country'] = 'USA'
        print(record)
       
        if current_year == 2021:
            final_result_22.append(record)
            print("Appended to 2022.")
        if current_year == 2022:
            final_result_21.append(record)
            print("Appended to 2021.")
        count += 1
        if count == 500:
            break
    print(final_result_21)
    print(final_result_22)
    collection21.insert_many(final_result_21)
    collection22.insert_many(final_result_22)
