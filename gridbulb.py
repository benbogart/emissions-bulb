from requests.api import get
import tinytuya
import json
import requests
from requests.auth import HTTPBasicAuth
from time import sleep


SCALING_FACTOR = 255/100 # adjust to limit color range
UPDATE_FREQUENCY = 300 # seconds between updates

LATITUDE = [YOUR LATITUDE]
LONGITUDE = [YOUR LONGITUDE]

WATTTIME_USERNAME = '[YOUR WATTTIME USERNAME]'
WATTTIME_PASSWORD = '[YOUR WATTTIME PASSWORD]'

BULB_DEVICE_ID = '[YOUR BULBS DEVICE ID]' # string
BULB_ADDRESS = '[YOUR BULBS IP ADDRESS]' # string
BULB_LOCAL_KEY = '[YOUR BULBS LOCAL KEY]' # string
BULB_VERSION = [YOUR BULBS VERSION] # as float (without '')


def get_bulb():
    bulb = tinytuya.BulbDevice(BULB_DEVICE_ID, BULB_ADDRESS, BULB_LOCAL_KEY)
    bulb.set_version(3.3)
    return bulb


def get_watttime_token():
    login_url = 'https://api2.watttime.org/v2/login'
    auth = HTTPBasicAuth(WATTTIME_USERNAME, WATTTIME_PASSWORD)
    rsp = requests.get(login_url, auth=auth)
    token = rsp.json()['token']

    return token


def get_watttime_pct():
    
    token = get_watttime_token()
    headers = {'Authorization': 'Bearer {}'.format(token)}
    index_url = 'https://api2.watttime.org/index'
    params = {'latitude': LATITUDE, 
              'longitude': LONGITUDE,}
    
    rsp=requests.get(index_url, headers=headers, params=params)
    percent = json.loads(rsp.text)['percent']
    return int(percent)

def calculate_rgb(watttime_pct):
    r = watttime_pct * SCALING_FACTOR
    g = 255 - r
    b = 0
    
    return r,g,b

# repeat forever
while True:
    bulb = get_bulb()
    watttime_pct = get_watttime_pct()
    r,g,b = calculate_rgb(watttime_pct)
    bulb.set_colour(r,g,b)
    sleep(UPDATE_FREQUENCY)