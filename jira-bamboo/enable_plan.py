#!/usr/bin/env python3

import json
import requests
import sys

build_key = sys.argv[1]

URL_BAMBOO_PLAN = "http://bamboo/rest/api/latest/plan/"
HEADERS = {
    'authorization': "Basic Secret-String"
    }

def enable_job(build_key):
    '''
    Enable disabled job
    '''
    url = URL_BAMBOO_PLAN + "%s.json" % build_key
    response = requests.request("GET", url)
    is_enabled = json.loads(response.text)['enabled']
    if not is_enabled:
        url = URL_BAMBOO_PLAN + "%s/enable" % build_key
        response = requests.request("POST", url, headers=HEADERS)


enable_job(build_key)
