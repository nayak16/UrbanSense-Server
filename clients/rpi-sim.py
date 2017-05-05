#!/usr/bin/env python

from influxdb import InfluxDBClient

import time
import random
import requests

print "I am a Raspberry Pi, please don't eat me..."
time.sleep(2)
# generate dummy data
data=[]
lat=40.443929
lng=-79.950668
t = int(time.time())
for i in xrange(100):
	lat += random.uniform(-0.001,0.001)
	lng += random.uniform(-0.001,0.001)
	value = random.uniform(1,4)
	t+=1
	data.append({
		"sensor_id": "0",
        "proc_id": 1, 
        "timestamp": t,
        "value": value,
        "lat": lat,
        "lng": lng,
        "tag_id": 1
    })

body = {
    "data_points": data
}
r = requests.post('http://localhost:5000/write', json=body)
if r.status_code != 200:
    raise Exception("POST not successful: {}".format(r.text))

print "Wrote 100 points to alpha"
