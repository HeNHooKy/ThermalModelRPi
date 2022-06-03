import serial
import math
import time
import re
import requests
import json
import urllib.request
from datetime import datetime
from pathlib import Path

ip = 'http://localhost'
port = 5055
code = 'utf-8'

coms = ['COM5']
boudrate = 9600

connectionList = []
for com in coms:
    ser = serial.Serial(com, boudrate, timeout=1)
    connectionList.append(ser)

#Проверяет, не отвалилось ли какое-нибудь подключение
def AreAlive(connectionList):
    for connection in connectionList:
        if not connection.is_open:
            return False
    return True

def GetId():
    file = Path('uuid.store')
    file.touch(exist_ok=True)

    f = open(file, 'r+')

    uuid = f.readline()
    print (uuid)

    if uuid == "":
        uuid = requests.get(f"{ip}:{str(port)}/Stores").text
        f.write(uuid)
    f.close()
    return uuid

def sendData(data):
    print(data)
    url = f'{ip}:{str(port)}/Stores'
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data, separators=(',', ':')), headers=headers)
    if r.status_code != 200:
        raise Exception(f'Error: server responses with code: {r.status_code}')

#Gets/reads raspberry pi id
piId = GetId()

time.sleep(2)
while AreAlive(connectionList):
    body = {
        'piid' : piId,
        'datas' : []
    }
    for connection in connectionList:
        line = connection.readline().decode(code)    #sensor line

        if not line: break
        if ";" not in line: break

        parts = line.strip().split(';')
        connectionNumber = int(parts[0])

        data = parts[1].split(',')

        body['datas'].append({
            'connectionNumber' : connectionNumber,
            'data' : data
        })

    if len(body['datas']) > 0:
        sendData(body)