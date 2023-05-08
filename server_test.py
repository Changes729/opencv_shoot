import requests
import time
point = [0.265625, 0.7458333333333333]
d={'x':point[0],'y':point[1]}
url='http://127.0.0.1:5000/setpoint'
while(1):
    # d = {'key1': 'value1', 'key2': 'value2'}
    r = requests.post(url, data=d)
    r = requests.get('http://127.0.0.1:5000')
    print(r.text)
    time.sleep(1)

