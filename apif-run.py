import argparse
import requests
import os.path
import json
import yaml
import sys
from functions import get_token, yaml_parser, set_method

pull_parser = argparse.ArgumentParser(description='APIF CLI Tool.')
pull_parser.add_argument('method', action="store", type=str, choices=['run-all', 'run-by-id', 'run-by-tag'], help="this is the type of run that you'll be performing.")
pull_parser.add_argument('hook', action="store", type=str, help="This is your webhook. It is required. It can be passed as either a URL, or a key from a configuration file.")
pull_parser.add_argument('-f', '--format', action="store", type=str,
                    help="This is the output format. Options are JSON, JUnit, or Bool")
pull_parser.add_argument('-S', '--Sync', const='?sync=true', nargs='?',
                    help="Sync mode. Waits for a response from the API route.")
pull_parser.add_argument('-d', '--dry', const='&dryrun=true', nargs='?', help='Dry run mode.')
pull_parser.add_argument('-s', '--silent', const='&silent=true', nargs='?', help='Silent mode')
pull_parser.add_argument('-o', '--out', action='store', type=str, help="output to directory")
pull_parser.add_argument('-c', '--config', action='store', type=str, help="path to config file. Defaults to ./config.yml")
pull_parser.add_argument('-C', '--credentials',
                    help='user credentials. overrides credentials present in config file <username:password>')
pull_parser.add_argument('-t', '--tag', action="store", type=str, help='a test tag')
pull_parser.add_argument('-i', '--id', action='store', type=str, help='a test id')

if len(sys.argv) == 1:
    pull_parser.print_help(sys.stderr)
    sys.exit(1)

args = pull_parser.parse_args()

config_key = None

web_hook = None

auth_token = None

if args.hook.startswith("http" or "https"):
    web_hook = args.hook
else:
    config_key = args.hook

if args.config:
    config_yaml = yaml_parser(os.path.join(args.config))

if config_key:
    if not args.config:
        config_yaml = yaml_parser(os.path.join('./config.yml'))
    for hook in config_yaml['hooks']:
        key = hook['key']
        if key == config_key:
            web_hook = hook['url']
            if not args.credentials:
                if "credentials" in hook:
                    config_credentials = (hook['credentials']['username'] + ":" + hook['credentials']['password'])
                    args.credentials = config_credentials

if args.credentials:
    auth_token = get_token(args.credentials, web_hook)

web_hook = set_method(args.method, web_hook, args.tag, args.id)

route_list = []

potential_args = [args.Sync, args.dry, args.silent, args.format]

for arg in potential_args:
    if arg:
        if arg == args.format:
            route_list.append('&format=' + args.format)
        else:
            route_list.append(arg)

for route in route_list:
    web_hook = web_hook + route

if auth_token:
    headers = {'Authorization': 'Bearer ' + auth_token}
    req = requests.get(web_hook, headers=headers)
    if req.status_code==200:
        print("APIF: OK")
    else: 
        print("APIF:" +str(req.status_code)+ " error")
elif web_hook:
    req = requests.get(web_hook)
    if req.status_code==200:
        print("APIF: OK")
    else: 
        print("APIF:" +str(req.status_code)+ " error")
if args.Sync:
    if req.headers["Content-Type"].startswith('application/json'):
        parsed_json = json.loads(req.content)
        print(json.dumps(parsed_json, indent=4))
    else:
        print(req.content)

if args.out:
    file = open(os.path.join(args.out), 'w')
    response_body = req.content
    file.write(response_body.decode('utf-8'))
