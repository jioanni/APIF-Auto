import os.path
import xml.etree.ElementTree as ET
import requests
import json
import sys
import yaml

## This is the function that generates a payload for the -p (path) tag.

def payload_builder(path, branch, payload):
        for root, dirs, files in os.walk(path):
            dir_name = root.split('/')[-2]
            for filename in files:
                if filename == ("unit.xml" or "input.xml"):
                    new_resource = {
                        "path" : "",
                        "branch" : "",
                        "revision" : "",
                        "content" : ""
                    }
                    with open(os.path.join(path + filename)) as stream:
                        try:
                            tree = ET.parse(stream)
                            root = tree.getroot()
                            xml_string = ET.tostring(root)
                        except ET.ParseError as exc:
                            print(exc, "This XML document is invalid.")
                    new_resource["path"] = dir_name + "/" + filename
                    new_resource["branch"] = branch
                    new_resource["content"] = xml_string
                    payload["resources"].append(new_resource)
                else:
                    continue

## This function allows us to generate an API Fortress security token based on the provided u/p combo.
#  If the credentials are bad, it will still carry out the API call, but in an unauthenticated fashion.

def get_token(credentials, hook):
    user_creds = credentials.split(":")
    auth_req = requests.get(hook + '/login', auth=(user_creds[0], user_creds[1]))
    access_token = auth_req.content
    parsed_token = json.loads(access_token)
    if not "access_token" in parsed_token: 
        print("Invalid credentials!")
        sys.exit(1)
        return None
    else:
        auth_token = parsed_token['access_token']
        return auth_token

## This function allows us to traverse through the filesystem past a given path and find all of the pertinent files. 

def traverser(route, branch, payload):
    for root, dirs, files in os.walk(route):
        dir_name = root.split('/')[-1]
        for next_file in files:
            acceptable = ['input.xml', "unit.xml"]
            if next_file in acceptable:
                new_resource = {
                        "path" : "",
                        "branch" : "",
                        "revision" : "",
                        "content" : ""
                    }
                with open(os.path.abspath(os.path.join(root + "/" + next_file))) as stream:
                    try:
                        tree = ET.parse(stream)
                        tree_root = tree.getroot()
                        xml_string = ET.tostring(tree_root)
                    except ET.ParseError as exc:
                            print(exc, "This XML document is invalid.")
                    new_resource["path"] = dir_name + "/" + next_file
                    new_resource["branch"] = branch
                    new_resource["content"] = xml_string
                    payload["resources"].append(new_resource)

## This function opens a given configuration yml and returns it as an iterable dictionary.

def yaml_parser(yml):
    with open(yml) as stream:
        try:
            config_yaml = (yaml.load(stream))
            return config_yaml
        except yaml.YAMLError as exc:
            print(exc)
            
##This function determines the method that we're using depending on the positional argument.

def set_method(method, hook, tag, id):
    if method == "run-all":
        return hook + '/tests/run-all'
    elif method == "run-by-tag":
        if tag:
            return hook + '/tests/tag/' + tag + "/run"
        else:
            print("Run by tag requires a tag (-t)")
            sys.exit(1)
    elif method == "run-by-id":
        if id:
            return hook + '/tests/' + id + "/run"
        else:
            print("Run by ID requires an ID (-i)")
            sys.exit(1)