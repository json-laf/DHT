# -*- coding : utf-8 -*-
# @Time : 2021/10/25 21:06
# @Author : Json
# @File : demo.py
# @Software : PyCharm

import aliyunsdkiotclient.AliyunIotMqttClient as iot
import json
import multiprocessing
import time, random

options = {
    'productKey': 'a1UyQPv6xXd',
    'deviceName': 'DHT_demo',
    'deviceSecret': '6c5052fac8c1bda352f678ddc10afe00',
    'port': 1883,
    'host': 'iot-as-mqtt.cn-shanghai.aliyuncs.com'
}


def GetDTH():
    return 1, 1


host = options['productKey'] + '.' + options['host']


def on_message(client, userdata, msg):
    print(msg.payload)
    setjson = json.loads(msg.payload)


def on_connect(client, userdata, flags_dict, rc):
    print("Connected with result code " + str(rc))


def on_disconnect(client, userdata, flags_dict, rc):
    print("Disconnected.")


def worker(client):
    topic = '/sys/' + options['productKey'] + '/' + options['deviceName'] + '/thing/event/property/post'
    while True:
        # file = open("/sys/class/thermal/thermal_zone0/temp", 'r')
        temp = random.randint(28, 30)
        # file.close()
        time.sleep(5)
        T, H = GetDTH()
        print('T=', T, 'H=', H)

        if T != 0 or H != 0:
            payload_json = {
                'id': int(time.time()),
                'params': {
                    'CurrentTemperature': temp,
                    'Temperature': random.randint(20, 30),
                    'Humidity': random.randint(40, 50),
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
    p.run()
    client.loop_forever()
