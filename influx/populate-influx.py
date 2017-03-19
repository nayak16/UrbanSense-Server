#!/usr/bin/env python

from influxdb import InfluxDBClient

import time
import random

print "Connecting to localhost:8086/alpha"
client = InfluxDBClient('localhost', 8086, database='alpha')
client.drop_database('alpha')
client.create_database('alpha')

# generate dummy data
json=[]
lat=40.443929
lng=-79.950668
t = int(time.time())
for i in xrange(100):
	lat += random.uniform(-0.001,0.001)
	lng += random.uniform(-0.001,0.001)
	value = random.uniform(1,4)
	t+=1
	json.append({
		"measurement": "ir",
        "tags": {
            "vehicleid": 1,
        },
        "time": t,
        "fields": {
            "value": value,
            "lat": lat,
            "lng": lng
        }
	})

client.write_points(json)
print "Wrote 100 points to alpha"
