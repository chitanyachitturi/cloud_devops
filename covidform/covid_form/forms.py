from flask import Blueprint, render_template, request, redirect, url_for, session, Response
from . import mongo
from datetime import datetime
from .createTestData import create_test_data, create_duplicate_test_data

import pandas as pd

covidForm = Blueprint('covidForm', __name__)
vaccine_range = ['1', '2', '3', '4']
y_n = ['yes', 'no']
month_map = {
    '01': 'January',
    '02': 'February',
    '03': 'March',
    '04': 'April',
    '05': 'May',
    '06': 'June',
    '07': 'July',
    '08': 'August',
    '09': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December'
}
allowed_symptoms = ['cough', 'cold', 'fever']


@covidForm.route('/', methods=['GET', 'POST'])
def covid_form():
    # get values from form and submit to database
    errors = []
    if request.method == 'POST':
        error = False
        
        collection = ''
        g_number = request.form.get('gNumber') or None
        if g_number is None:
            error = True
            errors.append('G number value is required.')

        name = request.form.get('name') or None
        if name is None or len(name) < 2:
            error = True
            errors.append('Name value is required. Value must be 2 characters minimum.')

        state = request.form.get('state') or None
        if state is None or len(state) < 2:
            error = True
            errors.append('State value is required.')

        country = 'USA'

        affected_date = request.form.get('affectedDate') or None
        if affected_date is None:
            error = True
            errors.append('Invalid affected date value.')
        else:
            affected_date = datetime.strptime(affected_date, '%Y-%m-%d')
            
            if affected_date.year == 2022:
                collection = get_collection_instance('formData22')
            if affected_date.year == 2021:
                collection = get_collection_instance('formData21')
            if collection == '':
                error = True
                errors.append('Invalid year selected for date. You can only select 2022 or 2021.');

        before_vaccines = request.form.get('beforeVaccines') or None
        if before_vaccines is None or before_vaccines not in vaccine_range:
            error = True
            errors.append('Invalid vaccines taken before affected value.')

        after_vaccines = request.form.get('afterVaccines') or None
        if after_vaccines is None or after_vaccines not in vaccine_range:
            error = True
            errors.append('Invalid vaccines taken after affected value.')

        on_campus_living = request.form.get('onCampusLiving') or None
        if on_campus_living is None or on_campus_living.lower() not in y_n:
            error = True
            errors.append('Invalid on campus living value.')

        parties_7_days = request.form.get('partiesAttendedInLast7Days') or None
        if parties_7_days is None or parties_7_days.lower() not in y_n:
            error = True
            errors.append('Invalid parties attended in last 7 days value.')

        hospitalized = request.form.get('hospitalized') or None
        if hospitalized is None or hospitalized.lower() not in y_n:
            error = True
            errors.append('Invalid hospitalized value.')

        recovery_days = request.form.get('recoveryDays') or None
        if recovery_days is None or (int(recovery_days) < 0 or int(recovery_days) > 60):
            error = True
            errors.append('Invalid recovery days value.')

        symptoms = request.form.getlist('symptoms') or None
        if symptoms is None:
            error = True
            errors.append('Please select symptoms.')

#Creating the duplicate student details
        if not error:
            student_collection = get_collection_instance('StudentDetails')
            _already_exist = collection.find_one({'gNumber': g_number})
            _existing_student = student_collection.find_one({'gNumber': g_number})
            if not _existing_student:
                import exrex #package used to generate random data.
                student = dict(
                    gNumber=g_number,
                    email=exrex.getone(
                        r'[a-z]{4,6}[0-9]{2,3}(@)(gmail|hotmail|yahoo|github|facebook|twitter|proto)\.(com)'
                    ),
                    phone_number=exrex.getone(r'\d{10}'),
                    state=state,
                    country=country
                )
                
                student_collection.insert_one(student)
            if _already_exist:
                
                errors = ['Record with same G number already exists for the selected year.']
            else:
                data = {
                    'gNumber': g_number,
                    'name': name,
                    'state': state,
                    'country': country,
                    'affectedDate': affected_date,
                    'beforeVaccines': int(before_vaccines),
                    'afterVaccines': int(after_vaccines),
                    'onCampusLiving': on_campus_living,
                    'partiesAttendedInLast7Days': parties_7_days,
                    'hospitalized': hospitalized,
                    'recoveryDays': int(recovery_days),
                    'symptoms': symptoms,
                }
                _created = collection.insert_one(data)
                
                return redirect(url_for('covidForm.success'))
    
    return render_template('index.html', err=errors)


@covidForm.route('/success')
def success():
    # Form submitted successfully
    return render_template('success.html')


@covidForm.route('/admin')
def admin():
    # fetches data from mongodb and renders it to admin.html page
    
    start = ''
    end = ''
    state = ''
    data_to_be_rendered = []
    errors = []
    error_g_num = ''
    msg = ''
    record_updated = False
    is_csv = False
    is_search = False

    # For search results
    if 'searchCollectionName' not in session.keys():  # set default value
        session['searchCollectionName'] = 'formData22'
    elif 'searchCollectionName' in request.args.keys():  # set value passed by user
        session['searchCollectionName'] = request.args.get('searchCollectionName')

    # For filter results
    if 'currentCollection' not in session.keys():  # set default value
        session['currentCollection'] = 'formData22'
    elif 'collectionName' in request.args.keys():  # set value passed by user
        session['currentCollection'] = request.args.get('collectionName')

    

    if 'search' in request.args.keys():
        is_search = True
        val = request.args.get('search')
        student_collection = get_collection_instance('StudentDetails')
        
        students = student_collection.aggregate([
            {
                '$match': {'$expr': {'$eq': ['$gNumber', val]}}
            },
            {
                '$lookup': {
                    'from': 'formData22',
                    'let': {'gNum': '$gNumber'},
                    'pipeline': [
                        {
                            '$match': {'$expr': {'$eq': ['$gNumber', '$$gNum']}}
                        }
                    ],
                    'as': 'data22'
                }
            },
        
            {
                '$lookup': {
                    'from': 'formData21',
                    'let': {'gNum': '$gNumber'},
                    'pipeline': [
                        {
                            '$match': {'$expr': {'$eq': ['$gNumber', '$$gNum']}}
                        }
                    ],
                    'as': 'data21'
                }
            },
        ])
        for s in students:
            s['data'] = [False, False]
            if len(s['data21']):
                s['data21'][0]['affectedDate'] = s['data21'][0]['affectedDate'].date()
                s['data21'][0]['symptoms'] = ", ".join(s['data21'][0]['symptoms'])
                s['data21'][0]['collection_name'] = 'formData21'
                s['data'][0] = s['data21'][0]
                s.pop('data21')
            if len(s['data22']):
                s['data22'][0]['affectedDate'] = s['data22'][0]['affectedDate'].date()
                s['data22'][0]['symptoms'] = ", ".join(s['data22'][0]['symptoms'])
                s['data22'][0]['collection_name'] = 'formData22'
                s['data'][1] = s['data22'][0]
                s.pop('data22')
            
            data_to_be_rendered.append(s)
    else:
        is_csv = True
        if 'startDate' in request.args.keys() and request.args.get('startDate'):
            start = datetime.strptime(request.args.get('startDate'), '%Y-%m-%d')
        if 'endDate' in request.args.keys() and request.args.get('endDate'):
            end = datetime.strptime(request.args.get('endDate'), '%Y-%m-%d')
        if 'state' in request.args.keys() and request.args.get('state'):
            state = request.args.get('state')

        collection = get_collection_instance(session['currentCollection'])

        if 'adminErrors' in session.keys():
            errors = session['adminErrors']
            session['adminErrors'] = []

        if 'errorGNumber' in session.keys():
            error_g_num = session['errorGNumber']
            session['errorGNumber'] = ''

        if 'recordUpdated' in session.keys():
            record_updated = session['recordUpdated']
            session['recordUpdated'] = False

        if 'recordUpdatedMessage' in session.keys():
            msg = session['recordUpdatedMessage']
            session['recordUpdatedMessage'] = ''

        session['adminDateQuery'] = {}

        if start or end or state:

            if state:
                session['adminDateQuery']['state'] = state

            if start and not end:
                session['adminDateQuery']['affectedDate'] = {'$gt': start}
            if not start and end:
                session['adminDateQuery']['affectedDate'] = {'$lt': end}
            if start and end:
                session['adminDateQuery']['affectedDate'] = {'$gt': start, '$lt': end}
            
            data = collection.find(session['adminDateQuery'])
        else:
            session['adminDateQuery'] = {}
            data = collection.find()

        for record in data:
            record['symptoms'] = ", ".join(record['symptoms'])
            record['affectedDate'] = record['affectedDate'].date()
            data_to_be_rendered.append(record)
    
    return render_template(
        'admin.html',
        data=data_to_be_rendered,
        errors=errors,
        gNum=error_g_num,
        updated=record_updated,
        updated_msg=msg,
        collection_name=session['currentCollection'],
        search_collection_name=session['searchCollectionName'],
        is_csv=is_csv,
        is_search=is_search,
    )


@covidForm.route('/downloadCsv')
def download_csv():
    records = get_collection_instance(session['currentCollection']).find(session['adminDateQuery'])
    df = pd.DataFrame(list(records))
    df.pop('_id')
    
    return Response(
        df.to_csv(),
        mimetype="text/csv",
        headers={
            "Content-disposition": "attachment; filename=Covid{name}.csv".format(
                name=session['currentCollection'].capitalize()
            )
        }
    )


@covidForm.route('/update', methods=['POST'])
def update():
    # This will update the record values from admin page and re-route back to admin.html page in future
    
    current_collection = request.form.get('collectionName')
    session['currentCollection'] = current_collection
    collection = get_collection_instance(current_collection)
    import bson
    record_id_to_update_delete = bson.ObjectId(request.args.get('id'))
    
    action = request.form.get('action').lower()
    if action == 'update':
        errors = []
        error = False

        name = request.form.get('name') or None
        if name is None or len(name) < 2:
            error = True
            errors.append('Name value is required and must be 2 characters minimum.')

        state = request.form.get('state') or None
        if state is None or len(state) < 2:
            error = True
            errors.append('State value is required.')

        country = 'USA'

        affected_date = request.form.get('affectedDate') or None
        if affected_date is None:
            error = True
            errors.append('Invalid affected date value.')
        else:
            affected_date = datetime.strptime(affected_date, '%Y-%m-%d')

        before_vaccines = request.form.get('beforeVaccines') or None
        if before_vaccines is None or before_vaccines not in vaccine_range:
            error = True
            errors.append('Invalid vaccines taken before affected value.')

        after_vaccines = request.form.get('afterVaccines') or None
        if after_vaccines is None or after_vaccines not in vaccine_range:
            error = True
            errors.append('Invalid vaccines taken after affected value.')

        on_campus_living = request.form.get('onCampusLiving') or None
        if on_campus_living is None or on_campus_living.lower() not in y_n:
            error = True
            errors.append('Invalid on campus living value.')

        parties_7_days = request.form.get('partiesAttendedInLast7Days') or None
        if parties_7_days is None or parties_7_days.lower() not in y_n:
            error = True
            errors.append('Invalid parties attended in last 7 days value.')

        hospitalized = request.form.get('hospitalized') or None
        if hospitalized is None or hospitalized.lower() not in y_n:
            error = True
            errors.append('Invalid hospitalized value.')

        recovery_days = request.form.get('recoveryDays') or None
        if recovery_days is None or (int(recovery_days) < 0 or int(recovery_days) > 60):
            error = True
            errors.append('Invalid recovery days value.')

        symptoms = request.form.get('symptoms') or None
        if symptoms is None:
            error = True
            errors.append('Please select symptoms.')
        elif ',' in symptoms:
            symptoms = [s.strip() for s in symptoms.split(sep=',')]
        else:
            symptoms = [symptoms]
        
        for s in symptoms:
            if s.lower() not in allowed_symptoms:
                error = True
                errors.append('Please input valid symptoms.')

        if not error:
            data = {
                'name': name,
                'state': state,
                'country': country,
                'affectedDate': affected_date,
                'beforeVaccines': int(before_vaccines),
                'afterVaccines': int(after_vaccines),
                'onCampusLiving': on_campus_living.capitalize(),
                'partiesAttendedInLast7Days': parties_7_days.capitalize(),
                'hospitalized': hospitalized.capitalize(),
                'recoveryDays': int(recovery_days),
                'symptoms': [s.capitalize() for s in symptoms],
            }
            _updated = collection.update_one({'_id': record_id_to_update_delete}, {'$set': data})
            
            session['recordUpdated'] = True
            session['recordUpdatedMessage'] = 'Record updated successfully!!'
        else:
            session['adminErrors'] = errors
            session['errorGNumber'] = request.form.get('gNumber')
    if action == 'delete':
        collection.delete_one({'_id': record_id_to_update_delete})
        session['recordUpdated'] = True
        session['recordUpdatedMessage'] = 'Record deleted successfully!!'
    return redirect(url_for('covidForm.admin'))


@covidForm.route('/userRecoveryCount')
def month_wise_user_recovered_in_given_days():
    year = request.args.get('forYear')
    
    if 'withinDays' in request.args.keys():
        within = request.args.get('withinDays')
    else:
        within = '14'
    collection = ''
    if year == '2021':
        collection = get_collection_instance('formData21')
    if year == '2022':
        collection = get_collection_instance('formData22')
    results = collection.aggregate([
        {
            '$match': {
                'recoveryDays': {
                    '$lte': int(within)
                }
            }
        },
        {
            '$group': {
                '_id': {'$dateToString': {'format': "%m", 'date': "$affectedDate"}},
                'count': {'$sum': 1}
            }
        }
    ])
    monthly_recovered_record_counts = {
        'January': 0,
        'February': 0,
        'March': 0,
        'April': 0,
        'May': 0,
        'June': 0,
        'July': 0,
        'August': 0,
        'September': 0,
        'October': 0,
        'November': 0,
        'December': 0,
    }
    for result in results:
        monthly_recovered_record_counts[
            month_map[result.get('_id')]
        ] = result['count']
    return monthly_recovered_record_counts


@covidForm.route('/stateWiseAffectedUsers')
def state_wise_affected_users():
    year = request.args.get('forYear')
    
    collection = ''
    if year == '2021':
        collection = get_collection_instance('formData21')
    if year == '2022':
        collection = get_collection_instance('formData22')
    results = collection.aggregate([
        {
            '$group': {
                '_id': '$state',
                'count': {'$sum': 1}
            }
        }
    ])
    state_response = []
    for result in results:
        result['state'] = result['_id']
        result.pop('_id')
        
        state_response.append(result)
    return state_response


@covidForm.route('/commonAffectedUsers')
def common_affected_users():
    collection = get_collection_instance('formData22')
    results = collection.aggregate([
        {
            '$lookup': {
                'from': 'formData21',
                'let': {'gNum': '$gNumber'},
                'pipeline': [
                    {
                        '$match': {'$expr': {'$eq': ['$gNumber', '$$gNum']}}
                    }
                ],
                'as': 'matchedDoc'
            }
        },
        {
            '$match': {'matchedDoc': {'$exists': True, '$ne': []}}
        },
        {
            '$group': {
                '_id': {
                    'gNumber': '$gNumber',
                    'hospitalizedIn2022': '$hospitalized',
                    'hospitalizedIn2021': '$matchedDoc.hospitalized'
                }
            }
        }
    ])
    response = dict(
        total_count=0,
        hospitalized_in_2022=0,
        hospitalized_in_2021=0,
        hospitalized_both_years=0,
        never_hospitalized=0
    )
    for result in results:
        response['total_count'] += 1
        r = result['_id']
        if r['hospitalizedIn2022'] == 'Yes' and r['hospitalizedIn2021'][0] == 'Yes':
            response['hospitalized_both_years'] += 1
        if r['hospitalizedIn2022'] == 'Yes' and r['hospitalizedIn2021'][0] == 'No':
            response['hospitalized_in_2022'] += 1
        if r['hospitalizedIn2022'] == 'No' and r['hospitalizedIn2021'][0] == 'Yes':
            response['hospitalized_in_2021'] += 1
        if r['hospitalizedIn2022'] == 'No' and r['hospitalizedIn2021'][0] == 'No':
            response['never_hospitalized'] += 1
        
    
    return response


@covidForm.route('/monthWiseHospitalizationCount')
def month_wise_hospitalization():
    # Line chart trend for count per month cases where user was hospitalized or not
    year = request.args.get('forYear')
    collection = ''
    if year == '2021':
        collection = get_collection_instance('formData21')
    if year == '2022':
        collection = get_collection_instance('formData22')
   
    monthly_hospitalization_record_counts = {
        'January': 0,
        'February': 0,
        'March': 0,
        'April': 0,
        'May': 0,
        'June': 0,
        'July': 0,
        'August': 0,
        'September': 0,
        'October': 0,
        'November': 0,
        'December': 0,
    }
    results = collection.aggregate([
        {
            '$group': {
                '_id': {
                    'hosp': '$hospitalized', 'date': "$affectedDate"
                },
                'hospitalizedCount': {'$sum': 1},
            }
        },
        {
            '$group': {
                '_id': {'$dateToString': {'format': "%m", 'date': "$_id.date"}},
                'hospitalized': {
                    '$push': {
                        'hosp': '$_id.hosp',
                        'count': '$hospitalizedCount'
                    }
                },
                'count': {'$sum': '$hospitalizedCount'},
            }
        }
    ])
    for result in results:
        hospitalized_data = result['hospitalized']
        response_map = {'Yes': 0, 'No': 0}
        for record in hospitalized_data:
            response_map[record['hosp']] += record['count']
        monthly_hospitalization_record_counts[
            month_map.get(result['_id'])  # Get month name
        ] = response_map  # set response to respective month in result
    
    return monthly_hospitalization_record_counts


def get_collection_instance(collection_name):
    if collection_name == 'formData22':
        return mongo.db.formData22
    if collection_name == 'formData21':
        return mongo.db.formData21
    if collection_name == 'StudentDetails':
        return mongo.db.StudentDetails
    return mongo.db.formData22


@covidForm.route('/statistics')
def stats():
    return render_template('statistics.html')

#triggering createTestData.py
@covidForm.route('/createTestData')
def create_test():
    if 'testCreated' not in session.keys():
        session['testCreated'] = False
    if not get_collection_instance('formData22').count_documents({}):
        session['testCreated'] = False
    if not session['testCreated']:
       
        create_test_data(get_collection_instance)
       
        create_duplicate_test_data(get_collection_instance)
        session['testCreated'] = True
        return {'inserted': True}
    else:
        return {'message': 'Data already exists.'}
