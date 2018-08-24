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




