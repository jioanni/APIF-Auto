#!/usr/bin/env python

import fileinput
import subprocess
import json
import requests
import yaml
import os


def choose_hook(branch):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.yml')) as stream:
            try:
                config_yaml = (yaml.load(stream))
            except yaml.YAMLError as exc:
                print(exc)
    for hook in config_yaml['hooks']:
        if "branch" in hook and branch == hook['branch']:
            return hook['url']


def post_receive(branch_name):
    print("APIF: Checking for modified")

    p = subprocess.Popen('git rev-parse --symbolic --abbrev-ref ' +branch_name, stdout=subprocess.PIPE, shell=True)
    branch_name = p.stdout.read().strip() 
    p = subprocess.Popen('git show ' + branch_name + ' --pretty="" --name-status', stdout=subprocess.PIPE, shell=True)
    files = p.stdout.read()
    files = files.strip().split('\n')
    body = {'resources' : []}

    # THIS IS WHERE THE PAYLOAD BUILDER WILL GO

    print('APIF: Updating ' +str(len(body['resources']))+" remote test files")
    if len(body['resources']) > 0:
        webhook = choose_hook(branch_name)
        params = json.dumps(body).encode('utf-8')

        req = requests.get(webhook + '/tests/push', headers = {"Content-Type" : 'application/json'}, data = params)

        if req.status_code==200:
            print("APIF: OK")
        else:
            print('APIF: ' + req.status_code + " error")


post_receive("master")