import os

from influxdb import InfluxDBClient

from flask import Flask, request, jsonify

from .exceptions import InvalidUsage
from .helpers import validate_json, success
import sensor_lut as lut

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'urbansense.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    INFLUX_HOST='localhost',
    INFLUX_PORT=8086,
    INFLUX_DB='beta'
))


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database...')


@app.cli.command('init_influx')
def init_influx_command():
	client = get_influx_client()
	client.drop_database('alpha')
	client.create_database('alpha')
	print 'Initialized InfluxDB...'


def get_influx_client():
	return InfluxDBClient(app.config['INFLUX_HOST'], app.config['INFLUX_PORT'], database=app.config['INFLUX_DB'])	

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/', methods=['GET', 'POST'])
def hello_world():
	print "asdfs"
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
			sensor_name, tag_name = lut.get_names(d['sensor_id'], d['tag_id'])
		except ValueError as e:
			print d
			raise InvalidUsage(e.message, status_code=400)
		except KeyError as e:
			print d
			raise InvalidUsage(
				"Sensor {} or Tag {} do not exist".format(d['sensor_id'], d['tag_id'])
				, status_code=400
			)

		if "inf" in str(d['value']):
			continue

		data_points.append({
				'measurement': sensor_name,
				'tags': {
					'sensor_id': d['sensor_id'],
					'proc_id': d['proc_id'],
					'tag_name': tag_name
				},
				'time': int(d['timestamp']),
				'fields': {
					'value': d['value'],
					'lat': d['lat'],
					'lng': d['lng']
				}
			}
		)

	client = get_influx_client()
	client.write_points(data_points)

	return success("Successfully wrote to InfluxDB")

