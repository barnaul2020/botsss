import itertools
import json
import random
import requests
from threading import Thread
from termcolor import colored

with open('config.json') as f:
    config = json.load(f)

proxy_list = config['proxy_list']
prefix_range = config['prefix_range']
middle_range = config['middle_range']
num_requests = config['num_requests']
block_number = config['block_number']

url = 'https://cstar.company/api/home/get_code'

data = {
    'username': '9835412541',
    'captcha': '6787',
    'cc': 'bp04hlwf',
    'prefix': '7'
}

log_file = open("requests.log", "a")

with open('keys.txt', 'r') as f:
    keys = f.read().splitlines()

for proxy in proxy_list:
    num_requests = num_requests  # Change this to the number of requests you want to send for each proxy
    thread = Thread(target=send_request, args=(proxy, num_requests, keys))
    threads.append(thread)
    thread.start()

def send_request(proxy, num_requests, keys):
    prefix_min, prefix_max = prefix_range
    middle_min, middle_max = middle_range

    for i in range(num_requests):
        first_digit = str(random.randint(prefix_min, prefix_max))
        third_digit = str(random.randint(middle_min, middle_max))
        share_code = ''.join([first_digit, block_number, third_digit])
        data['share_code'] = share_code
        print(f"Share code: {share_code}")

        try:
            response = requests.post(url, data=data, proxies={'https': proxy})

            log_file.write(f"\n\nRequest:\n{response.request.method} {response.request.url}\nHeaders: {response.request.headers}\nBody: {response.request.body}")
            log_file.write(f"\n\nResponse:\nStatus Code: {response.status_code}\nHeaders: {response.headers}\nContent: {response.text}")

            if "error_invite_code" in response.text:
                keys.remove(share_code)
                with open('keys.txt', 'w') as f:
                    f.write('\n'.join(keys))

            elif any(msg in response.text for msg in ["message.char_verify_code_error", "message.invalid_data"]):
                if "message.char_verify_code_error" in response.text:
                    print(colored(f"Share code: {share_code}", "green"))
                    with open('share_codes.txt', 'a') as file:
                        file.write(f"{share_code}\n")
                elif "message.invalid_data" in response.text:
                    captcha_url = f"https://cstar.company/api/home/get_captcha?cc={data['cc']}"
                    print(f"Invalid data response from {proxy}. Captcha URL: {captcha_url}")
                    captcha_response = requests.get(captcha_url, proxies={'https': proxy})
                    print(captcha_response.content)
            else:
                response_json = response.json()
                print(f"Response from {proxy.split(':')[-1]}: {response_json['msg']}")
        except:
            print(f"Error sending request with {proxy}")

threads = []

for proxy in proxy_list:
    num_requests = num_requests  # Change this to the number of requests you want to send for each proxy
    thread = Thread(target=send_request, args=(proxy, num_requests, keys))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

log_file.close()