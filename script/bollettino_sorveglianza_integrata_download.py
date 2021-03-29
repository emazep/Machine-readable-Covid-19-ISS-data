#
# -*- coding: utf-8 -*-
#
# Author: Emanuele Zeppieri <emazep@gmail.com>
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).
#

# Change this as needed
SAVE_PATH = '../original_ISS_documents/bollettino_sorveglianza_integrata/'
STOP_ON_FIRST_DUPLICATE = True # Stop as soon as an already downloaded doc is found locally.
WAIT = 5 # Seconds to wait for the next connetion; increase this in case you get:
# ConnectionError: ('Connection aborted.', ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None))
    
import requests
import time
import datetime as dt
from datetime import date, datetime, timedelta
import sys
import os
from colorama import init
from termcolor import colored

import locale
locale.setlocale(locale.LC_ALL, 'it_IT')

import functools
import os
import os
print = functools.partial(print, flush=True)

# Start and stop date to search ISS documents through.
# Keep in mind that if STOP_ON_FIRST_DUPLICATE is True, the script will exit at the first downloaded doc found locally.
start_date = dt.datetime.today().date()
stop_date = dt.date(2020, 3, 1)

URL_PREFIX = 'https://www.epicentro.iss.it/coronavirus/bollettino/'
FILE_PREFIX = 'Bollettino-sorveglianza-integrata-COVID-19_'
EXCEPTIONS = {
    dt.date(2020, 3, 26): 'Bollettino-sorveglianza-integrata-COVID-19_26-marzo 2020',
    dt.date(2020, 3, 23): 'Bollettino-sorveglianza-integrata-COVID-19_23-marzo 2020',
    dt.date(2020, 3, 16): 'Bollettino sorveglianza integrata COVID-19_16 marzo 2020',
    dt.date(2020, 3, 9): 'Bollettino-sorveglianza-integrata-COVID-19_09-marzo-2020'
}

# use Colorama to make Termcolor work on Windows too
init(autoreset=True)

strftime_char = '#' if os.name == 'nt' else '-'
strftime_string = f'%{strftime_char}d-%B-%Y'

s = requests.session()
s.keep_alive = False

d = 0 # Downloaded docs counter
scan_date = start_date

print('Checking ISS documents...')

while (scan_date >= stop_date):
    date_suffix_orig = scan_date.strftime(strftime_string)
    date_suffix_iso = scan_date.isoformat()
    
    file_original_name = EXCEPTIONS.get(scan_date, FILE_PREFIX + date_suffix_orig + '.pdf')
    file_normalized_name = FILE_PREFIX + date_suffix_iso + '.pdf'
    
    scan_date -= timedelta(days=1) # <- Keep exactly here!
    
    file_save_name = SAVE_PATH + file_normalized_name
    
    print()
    
    if os.path.exists(file_save_name):
        print(colored(file_save_name + '\talready present!', 'red', 'on_white'))
        if STOP_ON_FIRST_DUPLICATE:
            print('Exiting because an already downloaded doc has been found.\nTo scan every single date regardless of the already downloaded docs, please set STOP_ON_FIRST_DUPLICATE to False.')
            break
        continue
    
    time.sleep(WAIT)
    
    # ISS server lookup
    url = URL_PREFIX + file_original_name
    r = requests.get(url)
    content_type = r.headers.get('content-type')

    if 'application/pdf' not in content_type:
        print(colored(url + '\tnot found on server!', 'green', 'on_white'))
        continue
    
    with open(file_save_name, 'wb') as f:
        f.write(r.content)
        d += 1
        print(file_save_name, '\tSAVED')

print()
print('Done: ', start_date.isoformat(), '->', (scan_date+timedelta(days=1)).isoformat())
print(d, ' document(s) downloaded')
