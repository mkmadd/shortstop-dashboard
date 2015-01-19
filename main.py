# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 14:42:16 2015

@author: Administrator
"""

import bottle
import sys, os
import re
import gdata.docs.client, gdata.client
from natsort import natsorted
from itertools import groupby
from datetime import datetime, timedelta

ROW_RE = re.compile('<span>(.*?)</span>')
ALARM_DOC_NAME = 'Alarm Data' # google doc that stores alarm data
INV_DOC_NAME = 'Inventory Data' # google doc that stores inventory data
username = os.environ['GOOG_UID'] # google/gmail login id
password = os.environ['GOOG_PWD'] # google/gmail login password

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



def load_docs():
    client = gdata.docs.client.DocsClient(source='shortstop-dash')
    client.ssl= True
    
    try:
        client.ClientLogin(username, password, client.source);
    except (gdata.client.BadAuthentication, gdata.client.Error), e:
        sys.exit('ERROR: ' + str(e))
    except:
        sys.exit('ERROR: Unable to login')
    return client

def retrieve_doc(document_name):
    client = load_docs()
    doc_list = client.get_resources()
    docs = []
    for i in doc_list.entry:
        docs.append(i.title.text)
    doc_num = None
    for i, j in enumerate(docs):
        if j == document_name:
            doc_num = i
    if doc_num == None:
        return 0
        
    entry = doc_list.entry[doc_num]
    content = client.download_resource_to_memory(entry)
    rows = ROW_RE.findall(content)
    new_rows = []
    if rows:
        for row in rows:
            new_row = tuple(row.split('|'))
            new_rows.append(new_row)
    return new_rows


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
            new_tank['gross_volume'] = int(float(tank[3])) if tank[3] != 'None' else None
            new_tank['ullage'] = int(float(tank[4])) if tank[4] != 'None' else None
            new_tank['last_updated'] = datetime.strptime(tank[7], '%Y-%m-%d %H:%M:%S')
            new_tank['tank_low'] = False
            if name != 'Shortstop 25':
                warn_lvl = WARNING_LEVELS[name].get(new_tank['product_name'], 0)
            elif '1' not in new_tank['tank_name'] and \
                 '2' not in new_tank['tank_name']:
                warn_lvl = WARNING_LEVELS[name].get(new_tank['product_name'], 0)
            else:
                warn_lvl = 0
            if new_tank['gross_volume'] <= warn_lvl:
                new_tank['tank_low'] = True
            tank_info.append(new_tank)
            
        # Find the row with the earliest time to use at the last update
        earliest = min(tank_info, key=lambda x: x['last_updated'])
        store['last_update_time'] = earliest['last_updated'].strftime('%I:%M %p')
        store['last_update_date'] = earliest['last_updated'].strftime("%b %d, '%y")
        
        # If old date/time, set expired flags
        if earliest['last_updated'].date() != datetime.today().date():
            store['date_expired'] = True
        else:
            store['date_expired'] = False
        if (earliest['last_updated'] + timedelta(minutes=EXPIRED_TIME)) < datetime.now() - timedelta(hours=6):
            store['time_expired'] = True
        else:
            store['time_expired'] = False
            
        store['tanks'] = tank_info
        stores.append(store)
    return stores


@bottle.route('/')
@bottle.view('main')
def main():
    rows = retrieve_doc(INV_DOC_NAME)
    rows = natsorted(rows, key=lambda x: x[-1])
    alarms = retrieve_doc(ALARM_DOC_NAME)
    stores = format_stores(rows)
    return { 'stores': stores, 'alarms': alarms }
    
@bottle.route('/alarms')
@bottle.view('alarm')
def show_alarms():
    alarms = retrieve_doc(ALARM_DOC_NAME)
    alarms = natsorted(alarms, key=lambda x: x[0])
    #alarms = format_alarms(alarms)
    return { 'alarms': alarms }

app = bottle.default_app()
