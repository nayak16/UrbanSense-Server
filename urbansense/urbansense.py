import os

from flask import Flask, request, jsonify
from .exceptions import InvalidUsage
from .helpers import validate_json, success

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'urbansense.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    INFLUX_HOST='localhost',
    INFLUX_PORT=8086
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
	client = InfluxDBClient(app.config['INFLUX_HOST'], app.config['INFLUX_PORT'], database='alpha')
	client.drop_database('alpha')
	client.create_database('alpha')
	print 'Initialized InfluxDB...'


def get_influx_client():
	return InfluxDBClient(app.config['INFLUX_HOST'], app.config['INFLUX_PORT'], database='alpha')	

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
	return 'UrbanSense server ready to receive data...\n'

@app.route('/write', methods=['POST'])
def write_data():

	body = request.get_json()
	print body
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

	client = get_influx_client()
	client.write_points(data_points)

	return success("Successfully wrote to InfluxDB")

