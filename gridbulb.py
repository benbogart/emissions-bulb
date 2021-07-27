import tinytuya
import json
import pickle
import requests
from requests.auth import HTTPBasicAuth
from time import sleep
from datetime import datetime
import csv
import os


scaling_factor = 255/100 # adjust if you don't want to use the full color range
csv_cols = ["freq", "ba", "percent", "point_time"]
update_freq = 100

with open('passwords', 'rb') as f:
    username, password = pickle.load(f)

print('Establishing connection to bulb...')
b = tinytuya.BulbDevice('42313382e09806b2e707', '192.168.55.126', '34b08c42badc19b0')
b.set_version(3.3)
data = b.status()
print(f'set status result {data}')

def update_watttime_bulb(b):
    
    # reauthenticate watttime
    login_url = 'https://api2.watttime.org/v2/login'
    rsp = requests.get(login_url, auth=HTTPBasicAuth(username, password))
    token = rsp.json()['token']
    
    headers = {'Authorization': 'Bearer {}'.format(token)}
    ba = 'MISO_INDIANAPOLIS'

    index_url = 'https://api2.watttime.org/index'
    params = {'ba': ba}
    rsp=requests.get(index_url, headers=headers, params=params)
    
    wt = json.loads(rsp.text)
    global update_freq
    update_freq = int(wt['freq'])
    # log response
    # log setup
    write_header = False
    if not os.path.exists('log'):
        write_header = True
    
    with open('log', 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=wt.keys())
        if write_header:
            print('creating log file....')
            writer.writeheader()
        print(f'writing row: {wt}')
        writer.writerow(wt)
    
    
    pct = int(wt['percent'])
    
    r = pct * scaling_factor
    g = 255 - r
    
    return pct, b.set_colour(r,g,0)

for i in range(2):
    pct, result = update_watttime_bulb(b)
    
    # datetime object containing current date and time
    now = datetime.now()

    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    print(f'Iteration {i+1} ({dt_string}): {pct} pct')
    
    print(f'sleeping for {update_freq}')
    sleep(update_freq)