from flask import Flask, request, jsonify

def validate_json(json_blob):
	required_keys = ['value', 'lng', 'lat', 'proc_id', 'sensor_id', 'tag_id', 'timestamp']

	for key in required_keys:
		if key not in json_blob:
			print key
			raise ValueError("json missing key: {}".format(key))

def success(msg):
	return jsonify({'message':msg}), 200, {'ContentType':'application/json'}
