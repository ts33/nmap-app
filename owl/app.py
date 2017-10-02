import subprocess
import time
import requests
import os
import datetime
import concurrent.futures
from flask import Flask
app = Flask(__name__)


@app.route('/health')
def health():
    return 'Thank you, I am healthy'


scan_types = {
    'ACK':  '-sA',
    'SYN':  '-sS',
    'NULL': '-sN',
    'Xmas': '-sX'
}


def operate():
    num_threads = len(scan_types.keys())
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        for scan_name, scan_cmd in scan_types.items():
            executor.submit(loop_scan_and_post, scan_name, scan_cmd)


def loop_scan_and_post(scan_name, scan_cmd, scan_interval=60, ping_interval=10):
    while True:
        print(f'starting scan for {scan_name}')
        filename = generate_filename(scan_name)
        results = scan(scan_cmd, filename)

        while not ostrich_up():
            print(f'ostrich is not up... sleeping for {ping_interval} before sending results')
            time.sleep(ping_interval)

        print(f'ostrich is up... sending results for {scan_name}')
        status_code = post_to_ostrich(results)
        if status_code != 200:
            print(f'error sending results to ostrich for {scan_name}')

        time.sleep(scan_interval)


def scan(scan_cmd, filename):
    command = f"nmap -F {scan_cmd} -iL {os.environ['OWL_TARGET_FILE']} -oX {filename}"
    print(f'command : {command}')
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    _, error = process.communicate()

    if error is not None:
        raise Exception(f'Unable to run command : {command}')

    results = None
    with open(filename, 'r') as file:
        results = file.read()
    return results


def generate_filename(scan_name):
    return 'scans/' + datetime.datetime.now().strftime(f'%Y%m%d%H%M%S_{scan_name}')


def post_to_ostrich(content):
    r = requests.post(ostrich_url() + '/add', json={'content': content})
    return r.status_code


def ostrich_up():
    r = requests.get(ostrich_url() + '/health')
    if r.status_code == 200:
        return True
    else:
        return False


def ostrich_url():
    return f"http://{os.environ['OSTRICH_HOST']}:{os.environ['OSTRICH_PORT']}"


with app.app_context():
    required_variables = ['OSTRICH_HOST', 'OSTRICH_PORT', 'OWL_TARGET_FILE']
    if any(n not in os.environ for n in required_variables):
        raise Exception(f'One of the required environment variables are not set : {required_variables}')

    operate()
