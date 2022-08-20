import json

import requests


def _send_request(path, params=None, body=None, method='get'):
    url = "http://localhost:5000"
    try:
        if method == 'get':
            r = requests.get(url + path,
                             params=params,
                             headers={'Content-Type': 'application/json'},
                             data=body,
                             timeout=10)
        elif method == 'post':
            r = requests.post(url + path,
                              params=params,
                              headers={'Content-Type': 'application/json'},
                              data=body,
                              timeout=10)
        if method == 'put':
            r = requests.put(url + path,
                             params=params,
                             headers={'Content-Type': 'application/json'},
                             data=body,
                             timeout=10)
        if r.status_code == 200:
            return True, r.json()['data']
        else:
            print(r.status_code, r.json())
            return False, None
    except requests.exceptions.ConnectTimeout as e:
        print("timeout:", e)
        return False, None


def get_devices():
    return _send_request('/api/2/devices')


def get_device(mac):
    return _send_request('/api/2/devices/' + mac)


def device_join(mac):
    body = {
        "join": {
            'channels': [
                11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26
            ]
        }
    }
    return _send_request('/api/2/zigbees/' + mac, body=json.dumps(body), method='put')


def device_leave(mac):
    body = {
        "leave": {
        }
    }
    return _send_request('/api/2/zigbees/' + mac, body=json.dumps(body), method='put')


def zigbee_write(mac, attribute, value):

    payload = attribute.copy()
    payload['value'] = value
    body = {
        "attribute": payload
    }
    return _send_request('/api/2/zigbees/' + mac, body=json.dumps(body), method='put')


def device_data_request(mac):
    body = {
        "data_request": {
        }
    }
    return _send_request('/api/2/zigbees/' + mac, body=json.dumps(body), method='put')


def get_zigbee(mac):
    return _send_request('/api/2/zigbees/' + mac)


def get_zigbee_attribute(mac, attribute):
    params = attribute.copy()
    params['server'] = int(attribute['server'])
    params['manufacturer'] = int(attribute['manufacturer'])
    return _send_request('/api/2/zigbees/' + mac + '/attributes', params=params)


def get_attribute_value(mac, attribute):
    result, data = get_zigbee_attribute(mac, attribute)
    if result and data:
        return data
    else:
        return None
