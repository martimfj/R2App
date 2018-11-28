from flask import Flask, request, jsonify, make_response, render_template
from flask_pymongo import PyMongo
import os
import socket

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'reserveroom'
app.config['MONGO_URI'] = 'mongodb://mongo:27017/reserveroom'

mongo = PyMongo(app)
room = mongo.db.room

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({'message' : 'Running'}), 200

@app.route('/room', methods=['GET'])
def get_all_rooms():
    output = []
    for q in room.find():
        output.append({'name' : q['name'], 'room_type' : q['room_type'], 'floor' : q['floor'], 'capacity': q['capacity']})
    if output:
        return jsonify({'result' : output}), 200
    else:
        return jsonify({'message' : 'No results found'}), 204


@app.route('/room/<name>', methods=['GET'])
def get_one_room(name):
    if name:
        q = room.find_one({'name' : name})
        if q:
            return jsonify({'name' : q['name'], 'room_type' : q['room_type'], 'floor' : q['floor'], 'capacity': q['capacity']})
        else:
            return jsonify({'message' : 'No results found'}), 204
    else: 
        return jsonify({'message' : 'No data provided'}), 400


@app.route('/room', methods=['POST'])
def add_room():
    data = request.get_json()
    if data:
        name = request.json['name']
        room_type = request.json['room_type']
        floor = request.json['floor']
        capacity = request.json['capacity']
        existing_room = room.find_one({'name' : name})
        if existing_room is None:
            room.insert({'name' : name, 'room_type' : room_type, 'floor' : floor, 'capacity': capacity})
            return jsonify({'message' : 'Room <' + name  + '> created successfully'}), 201
        else:
            return jsonify({'message' : 'Room '< + name + '> already exists'}), 409
    else: 
        return jsonify({'message' : 'No data provided'}), 400     

@app.route('/room', methods=['PUT'])
def update_room():
    data = request.get_json()
    if data:
        name = request.json['name']
        existing_room = room.find_one({'name' : name})
        if existing_room:
            room_type = request.json['room_type']
            floor = request.json['floor']
            capacity = request.json['capacity']
            room.update_one({"name": name},
                            {"$set": {'room_type' : room_type, 'floor' : floor, 'capacity': capacity}})
            return jsonify({'message' : 'Room <' + name  + '> updated successfully'}), 200
        else:
            return jsonify({'message' : 'Room <' + name + '> does not exist'}), 409
    else: 
        return jsonify({'message' : 'No data provided'}), 400

@app.route('/room/<name>', methods=['DELETE'])
def delete_room(name):
    if name:
        existing_user = room.find_one({'name' : name})
        if existing_user:
            room.delete_one({"name": name})
            return jsonify({'message' : 'Room <' + name  + '> deleted successfully'}), 200
        else:
            return jsonify({'message' : 'Room <' + name + '> does not exist'}), 404
    else:
        return jsonify({'message' : 'No data provided'}), 400

@app.route('/', methods=['GET','POST'])
def main():
    error_message = ''
    if request.method == 'POST':
        data = request.form['name'] and request.form['room_type'] and request.form['floor'] and request.form['capacity']
        if data:
            name = request.form['name']
            room_type = request.form['room_type']
            floor = request.form['floor']
            capacity = request.form['capacity']
            existing_room = room.find_one({'name' : name})
            if existing_room is None:
                room.insert({'name' : name, 'room_type' : room_type, 'floor' : floor, 'capacity': capacity})
            else:
                error_message = 'Room ' + name + ' already exists'
        else: 
            error_message = 'Not all data was provided'

    output = []
    for q in room.find():
        output.append({'name' : q['name'], 'room_type' : q['room_type'], 'floor' : q['floor'], 'capacity': q['capacity']})
    
    process = os.getpid()
    hostname = socket.gethostname()

    return render_template('index.html', rooms=output, process=process, hostname=hostname, error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)