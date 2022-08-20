import json
import logging

import pytest
import requests
import time
import hmac
from hashlib import sha256

global token
global refresh_token
global gateway_vid
url = " https://openapi.tuyacn.com"
client_id = "fytdc8v4txurm79sskp3"
secret = "dwny8qy3s7epqqawcjqngqpe75mmmcsq"
schema = "sewiserdemo"
sign_method = "HMAC-SHA256"
uid = "ay1600225458332csTDL"
headers = {}


def _calculate_sign():
    timestamp = int(time.time() * 1000)
    plaintext = client_id + str(timestamp)
    global headers
    sign = hmac.new(secret.encode('utf-8'), plaintext.encode('utf-8'), digestmod=sha256).digest().hex().upper()
    headers = {
        "client_id": client_id,
        "sign": sign,
        "t": str(timestamp),
        "sign_method": sign_method
    }


def _calculate_sign_with_token():
    timestamp = int(time.time() * 1000)
    plaintext = client_id + token + str(timestamp)
    global headers
    sign = hmac.new(secret.encode('utf-8'), plaintext.encode('utf-8'), digestmod=sha256).digest().hex().upper()
    headers = {
        "client_id": client_id,
        "sign": sign,
        "t": str(timestamp),
        "sign_method": sign_method,
        "access_token": token
    }


def _send_request(path, params=None, body=None, method='get'):
    try:
        if method == "get":
            r = requests.get(url + path, params=params, headers=headers, timeout=10)
        elif method == "post":
            r = requests.post(url + path, params=params, headers=headers, data=body, timeout=10)
        elif method == "put":
            r = requests.put(url + path, params=params, headers=headers, data=body, timeout=10)
        elif method == "delete":
            r = requests.delete(url + path, params=params, headers=headers, data=body, timeout=10)
        if r.status_code == 200:
            response = r.json()
            if response['success']:
                return response['result']
            else:
                logging.warning("request failed:{}".format(response))
                if response['msg'] == 'token invalid':
                    # refresh token
                    if not _get_refresh_token():
                        logging.error("failed to refresh TUYA token")
                    else:
                        # resend command
                        _calculate_sign_with_token()
                        _send_request(path, params, body, method)
        else:
            print(r.status_code)
            return None
    except requests.exceptions.ConnectTimeout as e:
        print("timeout:", e)
        return None


def _get_token():
    _calculate_sign()
    params = {
        "grant_type": 1
    }
    result = _send_request('/v1.0/token', params=params)
    if result:
        global token
        global refresh_token
        token = result['access_token']
        refresh_token = result['refresh_token']
        print("token:", result['access_token'])
        print("refresh_token:", result['refresh_token'])
        return True
    else:
        print("get token failed")
        return False


def _get_refresh_token():
    _calculate_sign()
    global token
    global refresh_token
    result = _send_request('/v1.0/token/' + refresh_token)
    if result:
        token = result['access_token']
        refresh_token = result['refresh_token']
        print("token:", result['access_token'])
        print("refresh_token:", result['refresh_token'])
        return True
    else:
        print("get token failed")
        return False


def set_gateway_vid(vid):
    global gateway_vid
    gateway_vid = vid
    return _get_token()


def get_gateway_online_state():
    _calculate_sign_with_token()
    result = _send_request('/v1.0/devices/' + gateway_vid)
    if result:
        if result['online']:
            return True
        else:
            return False
    else:
        print('get gateway online state failed')
        return False


def get_gateway_permit_join_state():
    _calculate_sign_with_token()
    result = _send_request('/v1.0/devices/' + gateway_vid)
    if result:
        for status in result['status']:
            if status['code'] == 'permit_join':
                if status['value'] == 'true':
                    return True
                else:
                    return False
    else:
        print('get gateway permit join state failed')
        return False


def get_device_state(device):
    _calculate_sign_with_token()
    return _send_request('/v1.0/devices/' + device)


def get_sub_devices():
    _calculate_sign_with_token()
    return _send_request('/v1.0/devices/' + gateway_vid + '/sub-devices')


def delete_device(device):
    _calculate_sign_with_token()
    return _send_request('/v1.0/devices/' + device, method='delete')


def permit_join(duration=0):
    _calculate_sign_with_token()
    params = {
        "duration": duration
    }
    result = _send_request('/v1.0/devices/' + gateway_vid + '/enabled-sub-discovery',
                           params=params,
                           method='put')
    if result:
        return True
    else:
        print('permit join failed')
        return False


def device_command(device, code, value):
    _calculate_sign_with_token()
    body = {
        "commands": [
            {
                "code": code,
                "value": value
            }
        ]
    }
    result = _send_request('/v1.0/devices/' + device + '/commands',
                           body=json.dumps(body),
                           method='post')
    if result:
        return True
    else:
        print('send device command failed')
        return False


def get_status_value(device, code):
    device = get_device_state(device)
    if not device:
        return None
    else:
        for state in device['status']:
            if state['code'] == code:
                return state['value']
        print("failed to found {}".format(code))
        return None
