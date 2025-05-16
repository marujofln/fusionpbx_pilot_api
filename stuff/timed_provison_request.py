import os
import timeit

import requests
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')


def provision_request():
    """
    This function is a placeholder for the timed_provision_request function.

    """
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    r = requests.get('http://localhost:8000/v1/provisioning', headers=headers)
    return r.text


num = 3
total_time = 0
for i in range(num):
    start = timeit.default_timer()
    r = provision_request()
    end = timeit.default_timer()
    exec_time = end - start
    total_time += exec_time
    print(f'Execution time: {exec_time:.2f} seconds, return {r}')

print(f'Average execution time: {total_time / num:.2f} seconds')
