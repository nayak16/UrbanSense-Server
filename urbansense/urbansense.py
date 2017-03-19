from flask import Flask, request, jsonify
from .exceptions import InvalidUsage

app = Flask(__name__)

def validate_json(json_blob):
	required_keys = ['value', 'lng', 'lat', 'proc_id', 'sensor_name', 'timestamp']

	for key in required_keys:
		if key not in json_blob:
			raise ValueError("json missing key: {}".format(key))

def success(msg):
	return jsonify({'message':msg}), 200, {'ContentType':'application/json'} 

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/')
def hello_world():
	return 'UrbanSense server ready to receive data...\n'

@app.route('/write', methods=['POST'])
def write_data():

	body = request.get_json()
	if 'data_points' not in body:
		raise InvalidUsage('body must contain data_points key', status_code=400)

	data_points = []
	for d in body['data_points']:
		try:
			validate_json(d)
		except ValueError as e:
			raise InvalidUsage(e.message, status_code=400)

		data_points.append({
				'measurement': d['sensor_name'],
				'tags': {
					'proc_id': d['proc_id']
				},
				'time': d['timestamp'],
				'fields': {
					'value': d['value'],
					'lat': d['lat'],
					'lng': d['lng']
				}
			}
		)

	return success("Successfully wrote to DB")




	

