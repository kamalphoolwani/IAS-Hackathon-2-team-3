
from pydoc_data import topics
import sys
from flask import request
import kafka
from kafka import KafkaProducer
from kafka import KafkaConsumer
from time import sleep
import time
from datetime import datetime
import threading
from requests import get,post
import json
import dotenv
import os

dotenv.load_dotenv()

PORT_SLCM = os.getenv("SLCMIP")

kafka_ip = '20.219.107.251'
kafka_port = '9092'

registered_services = {}

def deregister(message):
    global registered_services
    print("deregister",message)
    data = {
        "instance_id" : message
    }
    print(data)
    post('http://{}/service_dead'.format(PORT_SLCM),json=data)
    del registered_services[message]

def log_reader():
    topic_name='logs'

    global registered_services
    consumer = KafkaConsumer(topic_name,bootstrap_servers='{}:{}'.format(kafka_ip,kafka_port),api_version = (0,10,1),)
    for message in consumer:
        msg=json.loads(message.value.decode('utf-8'))
        print(msg)
        if msg['type']=='flush':
            for k in list(registered_services.keys()):
                if time.time()-registered_services[k]>=15:
                    print("{} stopped working".format(k))
                    deregister(k)
        if msg['type']=='heartbeat':
            if msg['service_id'] not in registered_services.keys():
                print("new service started")
                registered_services[msg['service_id']] = time.time()
            else:
                registered_services[msg['service_id']] = time.time()
            
            continue

def register(message):
    registered_services[message['service_id']] = time.time()
    print(registered_services)

def flush():
    flush = KafkaProducer(bootstrap_servers='{}:{}'.format(kafka_ip,kafka_port),
                          api_version = (0,10,1),
                          value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    while True:
        flush.send('logs',{'type' : 'flush','service_id' : 0,'message' : '1'})
        time.sleep(10)


if __name__ == "__main__":

    threading.Thread(target=flush).start()
    log_reader()