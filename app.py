#!flask/bin/python
import json
import time
import datetime
import random
from flask import Flask,jsonify, abort, request, url_for
from flask_httpauth import HTTPBasicAuth
#
from db import db
series_collection = db.series_collection

app = Flask(__name__)

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

# find_document
def find_document(collection, elements, multiple=False):
    """ Function to retrieve a single or multiple documents from a provided
    collection using a dictionary containing a document's elements.
    """
    if multiple:
        results = collection.find(elements)
        return [r for r in results]
    else:
        return collection.find_one(elements)

# insert_document
def insert_document(collection, data):
    """ Function to insert a document into a collection and
    return the document's id.
    """
    return collection.insert_one(data).inserted_id

# update_document
def update_document(collection, query_elements, new_values):
    """ Function to update a single document in a collection.
    """
    return collection.update_one(query_elements, {'$set': new_values})

def delete_document(collection, query):
    """ Function to delete a single document from a collection.
    """
    collection.delete_one(query)

# make_public
def make_public_task(task):
    new_task = {}
    for field in task:
        if field == '_id':
            new_task['uri'] = url_for('get_task', task_id=task['_id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task

#
# auth
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'dev':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    # return make_response(jsonify({'error': 'Unauthorized access'}), 401)
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)

#

#def not_found(error):
#    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.route('/')
def index():
    return "Hello, World!"
#

# get tasks
# curl -i http://localhost:5000/todo/api/v1.0/tasks
# curl -u dev:python -i http://localhost:5000/todo/api/v1.0/tasks
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
# @auth.login_required
def get_tasks():
    # return Response(json.dumps(tasks),  mimetype='application/json')
    findresult = find_document(series_collection, {'view': 'all'}, True)
    if findresult:
        #publicfindresult = {'tasks': map(make_public_task, findresult)}
        return jsonify({'tasks': findresult})
    else:
        abort(404)

# by id
# curl -i http://localhost:5000/todo/api/v1.0/tasks/48676511168234
# curl -u dev:python -i http://localhost:5000/todo/api/v1.0/tasks/48676511168234
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
# @auth.login_required
def get_task(task_id):
    series = find_document(series_collection, {'_id': str(task_id)}, True)
    #task = list(filter(lambda t: t['_id'] == str(task_id), series))
    #if len(task) == 0:
    #    abort(404)
    return jsonify({'task': series[0]})

# post task
# curl -i -H "Content-Type: application/json" -X POST -d '{"name":"dev2","done":false,"year":1980}' http://localhost:5000/todo/api/v1.0/tasks
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
# @auth.login_required
def create_task():
    if not request.json or not 'name' in request.json:
        abort(400)
    task = {
        "_id": str(random.randrange(10**14)),
        "name": request.json['name'],
        "year": int(request.json['year']),
        'done': False,
        #'done': request.json['done'],
        'view': 'all',
        "date": st,
        'description': request.json.get('description', ""),
    }
    # tasks.append(task)
    id_ = insert_document(series_collection, task)
    return jsonify({'task': task, '_id': id_}), 201

# update
# curl -i -H "Content-Type: application/json" -X PUT -d '{"done":false}' http://localhost:5000/todo/api/v1.0/tasks/8027129821789
# curl -u dev:python -i -H "Content-Type: application/json" -X PUT -d '{"done":true}' http://localhost:5000/todo/api/v1.0/tasks/1591119179.306213989854592822964
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
@auth.login_required
def update_task(task_id):
    task = find_document(series_collection, {'_id': str(task_id)}, True)
    # task = filter(lambda t: t['_id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['name'] = request.json.get('name', task[0]['name'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    task[0]['dateUpdate'] = st

    #update_document(series_collection, {'_id': str(task_id)}, task[0])
    update_document(series_collection, {'_id': str(task[0].get('_id'))}, task[0])
    return jsonify({'task': task[0]})

# delete
# curl -i -H "Content-Type: application/json" -X DELETE -d '{"_id":"13773212836296"}' http://localhost:5000/todo/api/v1.0/tasks/52877473889703
# curl -u dev:python -i -H "Content-Type: application/json" -X DELETE -d '{"_id":"13773212836296"}' http://localhost:5000/todo/api/v1.0/tasks/1591119179.306213989854592822964
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
# @auth.login_required
def delete_task(task_id):
    #task = filter(lambda t: t['id'] == task_id, tasks)
    task = find_document(series_collection, {'_id': str(task_id)}, True)
    if (task[0]):
        delete_document(series_collection, {'_id': str(task[0].get('_id'))})
        return jsonify({'result': True, 'task': task[0], 'taskId': task[0].get('_id')})
        # _id = task[0]._id
    else:
        abort(404)

# Debug
if __name__ == '__main__':
    app.run(debug=True)
