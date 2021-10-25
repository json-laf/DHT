# -*- coding: utf-8 -*-
import aliyunsdkiotclient.AliyunIotMqttClient as iot
import json
import multiprocessing
import time
import random
import RPi.GPIO as GPIO

options = {
    "productKey": "a1UyQPv6xXd",
    "deviceName": "DHT_demo",
    "deviceSecret": "6c5052fac8c1bda352f678ddc10afe00",
    'port':1883,
    'host':'iot-as-mqtt.cn-shanghai.aliyuncs.com'
}


dht_pin =16
led_pin = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)

def GetDTH():	
	data = []
	j = 0 
	GPIO.setup(dht_pin, GPIO.OUT)
	GPIO.output(dht_pin, GPIO.LOW)
	time.sleep(0.02)
	GPIO.output(dht_pin, GPIO.HIGH)
	GPIO.setup(dht_pin, GPIO.IN)
	 
	while GPIO.input(dht_pin) == GPIO.LOW:
		continue
	while GPIO.input(dht_pin) == GPIO.HIGH:
		continue
	 
	while j < 40:
		k = 0
		while GPIO.input(dht_pin) == GPIO.LOW:
			continue
		while GPIO.input(dht_pin) == GPIO.HIGH:
			k += 1
			if k > 100:
				break
		if k < 8:
			data.append(0)
		else:
			data.append(1)
		j += 1
	 
	#print "sensor is working."
	#print data
	 
	humidity_bit = data[0:8]
	humidity_point_bit = data[8:16]
	temperature_bit = data[16:24]
	temperature_point_bit = data[24:32]
	check_bit = data[32:40]
	 
	humidity = 0
	humidity_point = 0
	temperature = 0
	temperature_point = 0
	check = 0
	 
	for i in range(8):
		humidity += humidity_bit[i] * 2 ** (7-i)
		humidity_point += humidity_point_bit[i] * 2 ** (7-i)
		temperature += temperature_bit[i] * 2 ** (7-i)
		temperature_point += temperature_point_bit[i] * 2 ** (7-i)
		check += check_bit[i] * 2 ** (7-i)
	 
	tmp = humidity + humidity_point + temperature + temperature_point
	if check == tmp:
		#print "temperature :", temperature, "*C, humidity :", humidity, "%"
		return temperature,humidity
	else:
		print("wrong")
		#print "temperature :", temperature, "*C, humidity :", humidity, "% check :", check, ", tmp :", tmp
		return 0,0
	

host = options['productKey'] + '.' + options['host']

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	#topic = '/' + productKey + '/' + deviceName + '/update'
    #{"method":"thing.service.property.set","id":"169885527","params":{"LED":1},"version":"1.0.0"}
    # print(msg.payload)
	setjson = json.loads(msg.payload)
	led = setjson['params']['LED']
	GPIO.output(led_pin,(GPIO.HIGH if led==1 else GPIO.LOW ))
    
def on_connect(client, userdata, flags_dict, rc):
	print("Connected with result code " + str(rc))
    
def on_disconnect(client, userdata, flags_dict, rc):
	print("Disconnected.")

def worker(client):
	topic = '/sys/'+options['productKey']+'/'+options['deviceName']+'/thing/event/property/post'
	while True:
		time.sleep(5)
        T,H = GetDTH()
        print('T=',T,'H=',H)
                         
        if T!=0 or H!=0:
            payload_json = {
                'id': int(time.time()),
                'params': {
                    'temperature':  T, #random.randint(20, 30),
                    'humidity':  H, #random.randint(40, 50)
                },
                'method': "thing.event.property.post"
                }
            
            print('send data to iot server: ' + str(payload_json))      
            client.publish(topic, payload=str(payload_json))
        

if __name__ == '__main__':
    client = iot.getAliyunIotMqttClient(options['productKey'], options['deviceName'], options['deviceSecret'], secure_mode=3)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(host=host, port=options['port'], keepalive=60)

    p = multiprocessing.Process(target=worker, args=(client,))
    p.start()
    client.loop_forever()
