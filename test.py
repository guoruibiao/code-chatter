# coding: utf8

# import server 
# app = server.Application(__name__)

# @app.route('/home')
# def home():
#     print("Home page is watching...")
#     yield "Home page...".encode('utf8')
# app.run()
import subprocess
import requests
import os
if os.path.exists('temp.py'):
    os.remove('temp.py')
url = "http://localhost:8888/api/user"

code = """
import datetime
print(datetime.datetime.now())
print(help(datetime)
"""
payload = {
    'code': code,
}

response = requests.post(url=url, data=payload)

print(response.text)

with open('temp.py', 'w', encoding='utf8') as f:
    f.write(response.text)


result = ''
p = subprocess.Popen('python temp.py', stdout=subprocess.PIPE)


result = p.stdout.read()
print(result)
