# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 14:42:16 2015

@author: Administrator
"""

import bottle
import re
import logging
from codecs import BOM_UTF8
from natsort import natsorted
from itertools import groupby
from datetime import datetime, timedelta
from pytz import timezone, utc

import httplib2

from apiclient import discovery, errors
import oauth2client
from oauth2client import client
from oauth2client import tools
from oauth2client.appengine import CredentialsNDBModel, StorageByKeyName

# had to change from <span> to <span class="c."> when Google docs suddenly 
# changed.  For some reason the class changes from c0 to c2
ROW_RE = re.compile(r'<span class="c.">(.*?)</span>')
ALARM_DOC_NAME = 'Alarm Data' # google doc that stores alarm data
INV_DOC_NAME = 'Inventory Data' # google doc that stores inventory data

SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Shortstop Dashboard'
ALARM_FILE_ID = '1kQ9Bfs7S-hd_NiPTZa0JQLYWg0FNVNgGl-9yRe3fI0c'
INV_FILE_ID = '1FfsSGg2XUExzPmggwvKSxRqG6sUnau7Ik53CSocKNjM'

EXPIRED_TIME = 20   # Number of minutes after which a time is expired

# From levels Marc sent
WARNING_LEVELS = {
    'Shortstop 1' : {
        'Unlead A, Unlead B' : 4128,
        'Prem.' : 500,
        'Diesel' : 716
    },
    'Shortstop 3' : {
        'Unlead' : 1453,
        'Premium' : 536,
        'Diesel' : 500
    },
    'Shortstop 4' : {
        'Unlead' : 3765,
        'Premium' : 771,
        'Diesel' : 3120
    },
    'Shortstop 8' : {
        'Unleaded' : 4815,
        'Premium' : 1012,
        'Diesel' : 2117,
        'Unlead WE' : 1404,
        'Unlead WW' : 3500,
        'Diesel West' : 742
    },
    'Shortstop 10' : {
        'Unleaded' : 4028,
        'Premium' : 790,
        'Diesel' : 874
    },
    'Shortstop 12' : {
        'Unleaded' : 4510,
        'Premium' : 622,
        'Diesel' : 657
    },
    'Shortstop 13' : {
        'Unleaded' : 9506,
        'Diesel' : 6622,
        'Premium' : 1133,
        'Def' : 1500
    },
    'Shortstop 16' : {
        'Unleaded' : 4998,
        'Premium' : 794,
        'Diesel' : 707
    },
    'Shortstop 18' : {
        'Unleaded' : 2782,
        'Premium' : 633,
        'Diesel' : 850
    },
    'Shortstop 20' : {
        'Unleaded' : 6991,
        'Premium' : 687,
        'Diesel' : 890,
        'Diesel LG' : 1235
    },
    'Shortstop 21' : {
        'Unleaded' : 2429,
        'Diesel' : 848
    },
    'Shortstop 22' : {
        'Unleaded' : 2360,
        'Premium' : 500,
        'Diesel, Diesel' : 3766
    },
    'Shortstop 23' : {
        'Unlead 1, Unlead 2' : 6972,
        'Premium' : 803,
        'Diesel' : 610
    },
    'Shortstop 24' : {
        'Unleaded A, Unleaded B' : 4356,
        'Premium' : 791,
        'Diesel A, Diesel B' : 4142
    },
    'Shortstop 25' : {
        'Unlead' : 2733,
        'Premium' : 528,
        'Diesel' : 3422
    },
    'Shortstop 26' : {
        'Unleaded' : 2107,
        'Premium' : 614,
        'E-15' : 589,
        'Diesel' : 768
    }
}

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
#    home_dir = os.path.expanduser('~')
#    credential_dir = os.path.join(home_dir, '.credentials')
#    if not os.path.exists(credential_dir):
#        os.makedirs(credential_dir)
#    credential_path = os.path.join(credential_dir,
#                                   'shortstop-dash.json')

    # Create Storage object associated with NDB datastore and get credentials
    storage = StorageByKeyName(CredentialsNDBModel, 
                               'shortstop_cred', 'credentials')
    credentials = storage.get()
    
    # If credentials not there, try to load from starter file
    if not credentials:
        store = oauth2client.file.Storage('shortstop-dash.json')
        credentials = store.get()
        storage.put(credentials)
        credentials = storage.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        flags = tools.argparser.parse_args(args=[])
        credentials = tools.run_flow(flow, storage, flags)
        if not credentials:
            logging.error('Could not obtain valid credentials')

#    storage.put(credentials)

    return credentials


def retrieve_doc(file_id):
    # Get credentials to access shortstop.dash account
    credentials = get_credentials()
    
    # Access shortstop.dash Google Drive
    http = httplib2.Http()
#    http = credentials.refresh(http)
    http = credentials.authorize(http)
    service = discovery.build('drive', 'v2', http=http)

    # Some code for listing all files and their ids in Google Drive
#    results = service.files().list().execute()
#    items = results.get('items', [])
#    for item in items:
#        logging.info('{0} ({1})'.format(item['title'], item['id']))

    # ...and try to get the meta info for the file we want
    try:
        file_meta = service.files().get(fileId=file_id).execute()
    except errors.HttpError, error:
        logging.error('An error occurred trying to get file: {}'.format(error))

    # Get the url for the file from its metadata, download it, and decode it
    dl_url = file_meta['exportLinks']['text/plain']

    resp, content = service._http.request(dl_url)
    content = content.lstrip(BOM_UTF8).decode('utf-8')
    
    # Data is pipe-delimited; split it up and format it into rows of tuples
    rows = [tuple(row.split('|')) for row in content.split('\r\n')]

    return rows


def fix_name(name):
    fixed_name = ''
    for word in name.strip().split():
        if len(word) > 2:
            word = word.capitalize()
        fixed_name += ' ' + word
    return fixed_name.strip()


# Format raw database output for consumption by index template
# 0. SITE_ID
# 1. STORAGE_ID
# 2. STORAGE_TYPE_ID
# 3. GROSS_VOLUME
# 4. ULLAGE
# 5. GROSS_WATER_VOLUME
# 6. WATER_LEVEL
# 7. LAST_UPDATED
# 8. NAME (tank)
# 9. PRODUCT_NAME
# 10. NAME (store)
def format_stores(rows):
    stores = []
    for name, tanks in groupby(rows, lambda x: x[10]):
        store = {}
        store['store_name'] = name
        
        tank_info = []
        for tank in tanks:
            new_tank = {}
            new_tank['site_id'] = tank[0]
            new_tank['storage_id'] = tank[1]
            new_tank['tank_name'] = fix_name(tank[8])
            new_tank['product_name'] = fix_name(tank[9])
            new_tank['gross_volume'] = int(float(tank[3])) \
                                       if tank[3] != 'None' else None
            new_tank['ullage'] = int(float(tank[4])) \
                                 if tank[4] != 'None' else None
            new_tank['last_updated'] = datetime.strptime(tank[7], 
                                                         '%Y-%m-%d %H:%M:%S')
            new_tank['tank_low'] = False
            if name != 'Shortstop 25':
                warn_lvl = WARNING_LEVELS[name].get(new_tank['product_name'], 
                                                    0)
            elif '1' not in new_tank['tank_name'] and \
                 '2' not in new_tank['tank_name']:
                warn_lvl = WARNING_LEVELS[name].get(new_tank['product_name'],
                                                    0)
            else:
                warn_lvl = 0
            if new_tank['gross_volume'] <= warn_lvl:
                new_tank['tank_low'] = True
            tank_info.append(new_tank)
            
        # Find the row with the earliest time to use at the last update
        earliest_row = min(tank_info, key=lambda x: x['last_updated'])
        central = timezone('US/Central')
        earliest = central.localize(earliest_row['last_updated'])
        store['last_update_time'] = earliest.strftime('%I:%M %p')
        store['last_update_date'] = earliest.strftime("%b %d, '%y")
        
        # Google App Engine time is UTC - adjust to CST
        adjusted_now = utc.localize(datetime.now()).astimezone(central)
        # If old date/time, set expired flags
        if earliest.date() != adjusted_now.date():
            store['date_expired'] = True
        else:
            store['date_expired'] = False
        if (earliest + timedelta(minutes=EXPIRED_TIME)) < adjusted_now:
            store['time_expired'] = True
        else:
            store['time_expired'] = False
            
        store['tanks'] = tank_info
        stores.append(store)
    return stores


@bottle.route('/')
@bottle.view('main')
def main():
    rows = retrieve_doc(INV_FILE_ID)
    rows = natsorted(rows, key=lambda x: x[-1])
    alarms = retrieve_doc(ALARM_FILE_ID)
    stores = format_stores(rows)
    return { 'stores': stores, 'alarms': alarms }

    
@bottle.route('/alarms')
@bottle.view('alarm')
def show_alarms():
    alarms = retrieve_doc(ALARM_FILE_ID)
    alarms = natsorted(alarms, key=lambda x: x[0])
    #alarms = format_alarms(alarms)
    return { 'alarms': alarms }

app = bottle.default_app()
bottle.debug(True)
