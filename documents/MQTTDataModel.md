 # MQTT Data Model v1.0
In ZLTH system, there are two role will folllow this specification for communication, Edge and Web

**topic**: {version}/{ip}/simulator[/{PATH}]\
**payload**:
```json
{
  "uuid": string,
  "timestamp": int,
  "data": {
    PAYLOAD
  }
}
```
## Edge
### client management
#### connected
**PATH**: /connected\
**PAYLOAD**:
```json
null
```
**target**: all\
**purpose**: send this message to announce edge connected
#### query
**PATH**: /sync\
**PAYLOAD**:
```json
{
  "ip": "{edge ip}"
}
```
**target**: edge who send /connected\
**purpose**: send this message to new edge to get edge info
#### query response
**PATH**: /synced\
**PAYLOAD**:
```json
{
  "ip": "{edge ip}",
  "mac": "{mac}",
  "label": "{label}",
  "version": "{version},",
  "name": "{name}",
  "connected": true,
  "broker": "{current connected MQTT broker IP}",
  "devices": ["{device mac}"]
}
```
**target**: edge who send /sync\
**purpose**: response /sync
#### status update
**PATH**: /update\
**PAYLOAD**:
```json
{
  "{attribute}": "{attribute value}"
}
```
attribute list:

attribute | type | description
--------- | ---- | -----------
connected | bool | edge connection status
label | string | user label
ip | string | edge ip
broker | string | edge connected MQTT broker

**target**: all\
**purpose**: notify to other edges that attribute update
#### command
**PATH**: /command\
**PAYLOAD**:
```json
{
  "{command name}": {command data}
}
```
command list:

**label**:
```json
{
  "data": "{user label}"
}
```
**firmware**:
```json
{
  "filename": "{filename}",
  "devices": ["{device mac}"]
}
```
**config**:
```json
{
  "config": {CONFIG_DATA},
  "devices": ["{device mac}"]
}
```
**CONFIG_DATA**:
```json
{
  "node": {
    "device_type": "{coordinator, router, end_device, sleepy_end_device}",
    "manufacturer_code": 4190,
    "radio_power": 10
  },
  "endpoints": [
    {
      "id": 1,
      "profile_id": 260,
      "device_id": 256,
      "server_clusters": [
        {
          "id": 0,
          "manufacturer": false,
          "manufacturer_code": 0,
          "name": "Basic",
          "attributes": [
            {
              "id": 0,
              "manufacturer": false,
              "manufacturer_code": 0,
              "type": "uint8",
              "writable": true,
              "length": 1,
              "default": 0,
              "name": "ZCL version"
            }
            ],
          "command": {
            "S->C": [
              {
                "id": 1,
                "manufacturer": true,
                "manufacturer_code": 4190,
                "description": "Test"
              }
            ],
            "C->S": [
              {COMMAND_DATA}
            ]
          }
        }
      ],
      "client_clusters": [
        {CLUSTER_DATA}
      ]
    }
  ]
}
```
**target**: edge should handle the command\
**purpose**: edge operation
### device management
#### connected
#### status change
#### query
### command
### error

## Web
### client management
### devce management