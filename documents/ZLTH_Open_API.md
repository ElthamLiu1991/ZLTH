---
title: Wiser-ZLTH v1.0.0
language_tabs:
  - shell: Shell
  - http: HTTP
  - javascript: JavaScript
  - ruby: Ruby
  - python: Python
  - php: PHP
  - java: Java
  - go: Go
toc_footers: []
includes: []
search: true
code_clipboard: true
highlight_theme: darkula
headingLevel: 2
generator: "@tarslib/widdershins v4.0.17"

---

# Wiser-ZLTH

> v1.0.0

Base URLs:

* <a href="http://localhost:5000/api/2">测试环境API2: http://localhost:5000/api/2</a>

# api/2/Devices

## GET 获取全部devices

GET /devices

> 返回示例

> 成功

```json
{
  "code": 0,
  "data": [
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEF12384",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM5",
      "label": ""
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEEE462C",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM24",
      "label": ""
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEEE4C05",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM13",
      "label": ""
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEF6DBD4",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM32",
      "label": ""
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEEE4599",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM12",
      "label": "label11"
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEF13008",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM19",
      "label": ""
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEEE4CE6",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM16",
      "label": ""
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEF6E634",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM15",
      "label": ""
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEF12436",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM18",
      "label": ""
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEF117E8",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM17",
      "label": ""
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEF123B1",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM23",
      "label": ""
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEF12BB5",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM14",
      "label": ""
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEF11851",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM22",
      "label": ""
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEEE461D",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM21",
      "label": ""
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEF6DAE9",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM11",
      "label": "label test"
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEF126E7",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM38",
      "label": ""
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEF12ABF",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM6",
      "label": "label"
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEF1343C",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM3",
      "label": ""
    },
    {
      "ip": "192.168.121.51",
      "configured": true,
      "hwversion": "1.0.0",
      "mac": "94DEB8FFFEF112DA",
      "connected": true,
      "state": 1,
      "swversion": "000103",
      "name": "COM46",
      "label": ""
    }
  ],
  "timestamp": 1653960392861,
  "uuid": "b46547ad-e080-11ec-bea7-1826492a4080",
  "message": ""
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||error code|
|» data|[object]|true|none||response data|
|»» configured|boolean|true|none||configuration state|
|»» connected|boolean|true|none||connection state: online/offline|
|»» hwversion|string|true|none||hardware version|
|»» ip|string|true|none||simulator IP address|
|»» label|string|true|none||user label|
|»» mac|string|true|none||ZIGBEE mac address|
|»» name|string|true|none||serial port name: tty/COM|
|»» state|integer|true|none||working state1: Uncommissioned2: Bootloader3: Upgrading4: Pairing5: Commissioning6: Joined7: Orphan8: Leaving9: Configuring|
|»» swversion|string|true|none||firmware version|
|» message|string|true|none||error description|
|» timestamp|integer|true|none||time stamp of this request|
|» uuid|string|true|none||request uuid|

## GET 按照MAC地址获取一个device

GET /devices/{mac}

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|mac|path|string| 是 |ZIGBEE MAC address|

> 返回示例

> 成功

```json
{
  "code": 0,
  "data": {
    "ip": "192.168.121.51",
    "configured": true,
    "hwversion": "1.0.0",
    "mac": "94DEB8FFFEF12384",
    "connected": true,
    "state": 1,
    "swversion": "000103",
    "name": "COM5",
    "label": ""
  },
  "timestamp": 1653962520435,
  "uuid": "a88743ba-e085-11ec-91b6-1826492a4080",
  "message": ""
}
```

> 记录不存在

```json
{
  "code": 10000,
  "message": "device 1122334455667788 not exist",
  "data": {}
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|记录不存在|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|»» ip|string|true|none||none|
|»» configured|boolean|true|none||none|
|»» hwversion|string|true|none||none|
|»» mac|string|true|none||none|
|»» connected|boolean|true|none||none|
|»» state|integer|true|none||none|
|»» swversion|string|true|none||none|
|»» name|string|true|none||none|
|»» label|string|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **404**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» message|string|true|none||none|
|» data|object|true|none||none|

## PUT 发送命令给指定的device

PUT /devices/{mac}

该接口支持发送identify, reset， 修改label等命令到device

> Body 请求参数

```json
{
  "label": {
    "data": "labore voluptate aute"
  },
  "reset": {},
  "identify": {}
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|mac|path|string| 是 |ZIGBEE mac address|
|body|body|object| 否 |none|
|» identify|body|object| 否 |identify request|
|» reset|body|object| 否 |reset request|
|» label|body|object| 否 |label modification request|
|»» data|body|string| 是 |label|

> 返回示例

> 成功

```json
{
  "code": 0,
  "message": "",
  "timestamp": 1654063999654,
  "uuid": "eedb3282-e171-11ec-865a-1826492a4080",
  "data": {}
}
```

> 记录不存在

```json
{
  "code": 10000,
  "data": {},
  "timestamp": 1654064037605,
  "uuid": "057a2375-e172-11ec-bb9d-1826492a4080",
  "message": "device 94DEB8FFFEF12AB not exist"
}
```

> 服务器内部错误

```json
{
  "code": 10001,
  "data": {},
  "timestamp": 1654064285247,
  "uuid": "99154351-e172-11ec-8cd7-1826492a4080",
  "message": "device 94DEB8FFFEF112DA is offline"
}
```

```json
{
  "code": 10002,
  "data": {},
  "timestamp": 1654064433434,
  "uuid": "f168b477-e172-11ec-a2e9-1826492a4080",
  "message": "device 94DEB8FFFEF112DA is in bootloader or upgrading mode"
}
```

```json
{
  "code": 90008,
  "message": "no response",
  "data": {},
  "timestamp": 1653630453988,
  "uuid": "81808529-dd80-11ec-840b-1826492a4080"
}
```

```json
{
  "code": 90002,
  "data": {},
  "timestamp": 1654071175835,
  "uuid": "a4317637-e182-11ec-8762-1826492a4080",
  "message": "unsupported command: identifyii"
}
```

```json
{
  "code": 90004,
  "data": {},
  "timestamp": 1654071247721,
  "uuid": "cf0a7354-e182-11ec-9069-1826492a4080",
  "message": "json validation failed:'data' is a required property"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|记录不存在|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|服务器内部错误|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **404**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **500**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## PUT 更新指定设备配置

PUT /devices/{mac}/config

> Body 请求参数

```json
{
  "config": {
    "endpoints": [
      {
        "client_clusters": [
          {
            "id": 25,
            "name": "Over-The-Air Upgrade",
            "manufacturer": false,
            "attributes": [
              {
                "id": 0,
                "name": "UpgradeServerID",
                "type": "EUI64",
                "writable": false,
                "default": 18446744073709552000,
                "manufacturer": false
              },
              {
                "id": 1,
                "name": "FileOffset",
                "type": "uint32",
                "writable": false,
                "default": 4294967295,
                "manufacturer": false
              },
              {
                "id": 2,
                "name": "CurrentFileVersion",
                "type": "uint32",
                "writable": false,
                "default": 4294967295,
                "manufacturer": false
              },
              {
                "id": 3,
                "name": "CurrentZigBeeStackVersion",
                "type": "uint16",
                "writable": false,
                "default": 65535,
                "manufacturer": false
              },
              {
                "id": 4,
                "name": "DownloadedFileVersion",
                "type": "uint32",
                "writable": false,
                "default": 4294967295,
                "manufacturer": false
              },
              {
                "id": 5,
                "name": "DownloadedZigBeeStackVersion",
                "type": "uint16",
                "writable": false,
                "default": 65535,
                "manufacturer": false
              },
              {
                "id": 6,
                "name": "ImageUpgradeStatus",
                "type": "enum8",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 7,
                "name": "ManufacturerID",
                "type": "uint16",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 8,
                "name": "ImageTypeID",
                "type": "uint16",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 9,
                "name": "MinimumBlockPeriod",
                "type": "uint16",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 10,
                "name": "ImageStamp",
                "type": "uint32",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 65533,
                "name": "ClusterRevision",
                "type": "uint16",
                "writable": false,
                "default": 1,
                "manufacturer": false
              }
            ],
            "commands": {
              "C->S": [
                {
                  "id": 1,
                  "description": "Query Next Image Request",
                  "manufacturer": false
                },
                {
                  "id": 3,
                  "description": "Image Block Request",
                  "manufacturer": false
                },
                {
                  "id": 6,
                  "description": "Upgrade End Request",
                  "manufacturer": false
                }
              ],
              "S->C": [
                {
                  "id": 0,
                  "description": "Image Notify",
                  "manufacturer": false
                },
                {
                  "id": 2,
                  "description": "Query Next Image Response",
                  "manufacturer": false
                },
                {
                  "id": 5,
                  "description": "Image Block Response",
                  "manufacturer": false
                },
                {
                  "id": 7,
                  "description": "Upgrade End Response",
                  "manufacturer": false
                },
                {
                  "id": 9,
                  "description": "Query Device Specific File Response",
                  "manufacturer": false
                }
              ]
            }
          }
        ],
        "device_id": 256,
        "device_version": 1,
        "id": 10,
        "profile_id": 260,
        "server_clusters": [
          {
            "id": 0,
            "name": "Basic",
            "manufacturer": false,
            "attributes": [
              {
                "id": 0,
                "name": "ZCLVersion",
                "type": "uint8",
                "writable": false,
                "default": 2,
                "manufacturer": false
              },
              {
                "id": 1,
                "name": "ApplicationVersion",
                "type": "uint8",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 2,
                "name": "StackVersion",
                "type": "uint8",
                "writable": false,
                "default": 2,
                "manufacturer": false
              },
              {
                "id": 3,
                "name": "HWVersion",
                "type": "uint8",
                "writable": false,
                "default": 1,
                "manufacturer": false
              },
              {
                "id": 4,
                "name": "ManufacturerName",
                "type": "string",
                "length": 32,
                "writable": false,
                "default": "Schneider Electric",
                "manufacturer": false
              },
              {
                "id": 5,
                "name": "ModelIdentifier",
                "type": "string",
                "length": 32,
                "writable": false,
                "default": "E8331SRY800ZB",
                "manufacturer": false
              },
              {
                "id": 6,
                "name": "DataCode",
                "type": "string",
                "length": 16,
                "writable": false,
                "default": "",
                "manufacturer": false
              },
              {
                "id": 7,
                "name": "PowerSource",
                "type": "enum8",
                "writable": false,
                "default": 1,
                "manufacturer": false
              },
              {
                "id": 10,
                "name": "ProductCode",
                "type": "octstr",
                "length": 16,
                "writable": false,
                "default": "",
                "manufacturer": false
              },
              {
                "id": 16384,
                "name": "SWBuildID",
                "type": "string",
                "length": 16,
                "writable": false,
                "default": "",
                "manufacturer": false
              },
              {
                "id": 57345,
                "name": "SoftwareVersionString",
                "type": "string",
                "length": 20,
                "writable": false,
                "default": "1.1.1",
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 57346,
                "name": "HardwareVersionString",
                "type": "string",
                "length": 20,
                "writable": false,
                "default": "1.1.1",
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 57348,
                "name": "SerialNumber",
                "type": "string",
                "length": 32,
                "writable": false,
                "default": "",
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 57351,
                "name": "ProductIdentifier",
                "type": "enum16",
                "writable": false,
                "default": 0,
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 57352,
                "name": "ProductRange",
                "type": "string",
                "length": 16,
                "writable": false,
                "default": "",
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 57353,
                "name": "ProductModel",
                "type": "string",
                "length": 16,
                "writable": false,
                "default": "",
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 57354,
                "name": "ProductFamily",
                "type": "string",
                "length": 16,
                "writable": false,
                "default": "Wiser Home",
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 57355,
                "name": "VendorURL",
                "type": "string",
                "length": 64,
                "writable": false,
                "default": "http://www.schneider-electric.com",
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 65533,
                "name": "ClusterRevision",
                "type": "uint16",
                "writable": false,
                "default": 0,
                "manufacturer": false
              }
            ],
            "commands": {
              "C->S": [
                {
                  "id": 0,
                  "description": "Reset to Factory Defaults",
                  "manatory": false,
                  "manufacturer": false
                }
              ],
              "S->C": []
            }
          },
          {
            "id": 3,
            "name": "Identify",
            "manufacturer": false,
            "attributes": [
              {
                "id": 0,
                "name": "IdentifyTime",
                "type": "uint16",
                "writable": true,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 65533,
                "name": "ClusterRevision",
                "type": "uint16",
                "writable": true,
                "default": 1,
                "manufacturer": false
              }
            ],
            "commands": {
              "C->S": [
                {
                  "id": 0,
                  "description": "Identify",
                  "manufacturer": false
                },
                {
                  "id": 1,
                  "description": "Identify Query",
                  "manufacturer": false
                }
              ],
              "S->C": [
                {
                  "id": 0,
                  "description": "Identify Query Response",
                  "manufacturer": false
                }
              ]
            }
          },
          {
            "id": 4,
            "name": "Groups",
            "manufacturer": false,
            "attributes": [
              {
                "id": 0,
                "name": "NameSupport",
                "type": "map8",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 65533,
                "name": "ClusterRevision",
                "type": "uint16",
                "writable": false,
                "default": 0,
                "manufacturer": false
              }
            ],
            "commands": {
              "C->S": [
                {
                  "id": 0,
                  "description": "Add group",
                  "manufacturer": false
                },
                {
                  "id": 1,
                  "description": "View group",
                  "manufacturer": false
                },
                {
                  "id": 2,
                  "description": "Get group membership",
                  "manufacturer": false
                },
                {
                  "id": 3,
                  "description": "Remove group",
                  "manufacturer": false
                },
                {
                  "id": 4,
                  "description": "Remove all groups",
                  "manufacturer": false
                },
                {
                  "id": 5,
                  "description": "Add group if identifying",
                  "manufacturer": false
                }
              ],
              "S->C": [
                {
                  "id": 0,
                  "description": "Add group response",
                  "manufacturer": false
                },
                {
                  "id": 1,
                  "description": "View group response",
                  "manufacturer": false
                },
                {
                  "id": 2,
                  "description": "Get group membership response",
                  "manufacturer": false
                },
                {
                  "id": 3,
                  "description": "Remove group response",
                  "manufacturer": false
                }
              ]
            }
          },
          {
            "id": 5,
            "name": "Scenes",
            "manufacturer": false,
            "attributes": [
              {
                "id": 0,
                "name": "SceneCount",
                "type": "uint8",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 1,
                "name": "CurrentScene",
                "type": "uint8",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 2,
                "name": "CurrentGroup",
                "type": "uint16",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 3,
                "name": "SceneValid",
                "type": "bool",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 4,
                "name": "NameSupport",
                "type": "map8",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 65533,
                "name": "ClusterRevision",
                "type": "uint16",
                "writable": false,
                "default": 0,
                "manufacturer": false
              }
            ],
            "commands": {
              "C->S": [
                {
                  "id": 0,
                  "description": "Add Scene",
                  "manufacturer": false
                },
                {
                  "id": 1,
                  "description": "View Scene",
                  "manufacturer": false
                },
                {
                  "id": 2,
                  "description": "Remove Scene",
                  "manufacturer": false
                },
                {
                  "id": 3,
                  "description": "Remove All Scenes",
                  "manufacturer": false
                },
                {
                  "id": 4,
                  "description": "Store Scene",
                  "manufacturer": false
                },
                {
                  "id": 5,
                  "description": "Recall Scene",
                  "manufacturer": false
                },
                {
                  "id": 6,
                  "description": "Get Scene Membership",
                  "manufacturer": false
                }
              ],
              "S->C": []
            }
          },
          {
            "id": 6,
            "name": "On/Off",
            "manufacturer": false,
            "attributes": [
              {
                "id": 0,
                "name": "OnOff",
                "type": "bool",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 65533,
                "name": "ClusterRevision",
                "type": "uint16",
                "writable": false,
                "default": 1,
                "manufacturer": false
              }
            ],
            "commands": {
              "C->S": [
                {
                  "id": 0,
                  "description": "Off",
                  "manufacturer": false
                },
                {
                  "id": 1,
                  "description": "On",
                  "manufacturer": false
                },
                {
                  "id": 2,
                  "description": "Toggle",
                  "manufacturer": false
                }
              ],
              "S->C": []
            }
          },
          {
            "id": 64516,
            "name": "Visa Configuration",
            "manufacturer": true,
            "manufacturer_code": 4190,
            "attributes": [
              {
                "id": 0,
                "name": "IndicatorLuminanceLevel",
                "type": "uint8",
                "writable": true,
                "default": 0,
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 1,
                "name": "IndicatorColor",
                "type": "uint8",
                "writable": true,
                "default": 0,
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 2,
                "name": "Indicator Mode",
                "type": "uint8",
                "writable": true,
                "default": 0,
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 65533,
                "name": "ClusterRevision",
                "type": "uint16",
                "writable": true,
                "default": 1,
                "manufacturer": true,
                "manufacturer_code": 4190
              }
            ],
            "commands": {
              "C->S": [],
              "S->C": []
            }
          }
        ]
      }
    ],
    "node": {
      "device_type": "router",
      "manufacturer_code": 4190,
      "radio_power": 10
    }
  }
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|mac|path|string| 是 |none|
|body|body|object| 否 |none|
|» filename|body|string| 否 |filename from config file list|
|» config|body|object| 否 |config detail|
|»» endpoints|body|[object]| 是 |none|
|»»» client_clusters|body|[object]| 否 |none|
|»»»» attributes|body|[object]| 是 |none|
|»»»»» default|body|any| 是 |none|
|»»»»»» *anonymous*|body|string| 否 |none|
|»»»»»» *anonymous*|body|integer| 否 |none|
|»»»»» id|body|integer| 是 |none|
|»»»»» length|body|integer| 否 |none|
|»»»»» manufacturer|body|boolean| 是 |none|
|»»»»» manufacturer_code|body|integer| 否 |none|
|»»»»» name|body|string| 是 |none|
|»»»»» type|body|string| 是 |none|
|»»»»» writable|body|boolean| 是 |none|
|»»»» commands|body|object| 是 |none|
|»»»»» C->S|body|[object]| 是 |none|
|»»»»»» description|body|string| 是 |none|
|»»»»»» id|body|integer| 是 |none|
|»»»»»» manufacturer|body|boolean| 是 |none|
|»»»»»» manufacturer_code|body|integer| 否 |none|
|»»»»» S->C|body|[object]| 是 |none|
|»»»»»» description|body|string| 是 |none|
|»»»»»» id|body|integer| 是 |none|
|»»»»»» manufacturer|body|boolean| 是 |none|
|»»»»»» manufacturer_code|body|integer| 否 |none|
|»»»» id|body|integer| 是 |none|
|»»»» manufacturer|body|boolean| 是 |none|
|»»»» manufacturer_code|body|integer| 否 |none|
|»»»» name|body|string| 是 |none|
|»»» device_id|body|integer| 否 |none|
|»»» device_version|body|integer| 否 |none|
|»»» id|body|integer| 否 |none|
|»»» profile_id|body|integer| 否 |none|
|»»» server_clusters|body|[object]| 否 |none|
|»»»» attributes|body|[object]| 是 |none|
|»»»»» default|body|any| 是 |none|
|»»»»»» *anonymous*|body|string| 否 |none|
|»»»»»» *anonymous*|body|integer| 否 |none|
|»»»»» id|body|integer| 是 |none|
|»»»»» length|body|integer| 否 |none|
|»»»»» manufacturer|body|boolean| 是 |none|
|»»»»» manufacturer_code|body|integer| 否 |none|
|»»»»» name|body|string| 是 |none|
|»»»»» type|body|string| 是 |none|
|»»»»» writable|body|boolean| 是 |none|
|»»»» commands|body|object| 是 |none|
|»»»»» C->S|body|[object]| 是 |none|
|»»»»»» description|body|string| 是 |none|
|»»»»»» id|body|integer| 是 |none|
|»»»»»» manufacturer|body|boolean| 是 |none|
|»»»»»» manufacturer_code|body|integer| 否 |none|
|»»»»» S->C|body|[object]| 是 |none|
|»»»»»» description|body|string| 是 |none|
|»»»»»» id|body|integer| 是 |none|
|»»»»»» manufacturer|body|boolean| 是 |none|
|»»»»»» manufacturer_code|body|integer| 否 |none|
|»»»» id|body|integer| 是 |none|
|»»»» manufacturer|body|boolean| 是 |none|
|»»»» manufacturer_code|body|integer| 否 |none|
|»»»» name|body|string| 是 |none|
|»» node|body|object| 是 |none|
|»»» device_type|body|string| 是 |none|
|»»» manufacturer_code|body|integer| 是 |none|
|»»» radio_power|body|integer| 是 |none|

> 返回示例

> 成功

```json
{
  "code": 0,
  "message": "",
  "timestamp": 1655085078308,
  "uuid": "512923b8-eabb-11ec-9f94-1826492a4080",
  "data": {}
}
```

> 记录不存在

```json
{
  "code": 10000,
  "data": {},
  "timestamp": 1654760123693,
  "uuid": "b91de6fe-e7c6-11ec-a0cc-1826492a4080",
  "message": "device 94DEB8FFFEF11F3 not exist"
}
```

> 服务器内部错误

```json
{
  "code": 91000,
  "message": "no response",
  "timestamp": 1654760086638,
  "uuid": "a307c13c-e7c6-11ec-91b9-1826492a4080",
  "data": {}
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|记录不存在|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|服务器内部错误|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» message|string|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» data|object|true|none||none|

状态码 **404**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **500**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## GET 获取设备配置信息

GET /devices/{mac}/config

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|mac|path|string| 是 |none|

> 返回示例

> 成功

```json
{
  "code": 0,
  "message": "",
  "timestamp": 1655176637857,
  "uuid": "7ee7a475-eb90-11ec-8ba8-1826492a4080",
  "data": {
    "config": {
      "node": {
        "device_type": "router",
        "radio_power": 10,
        "manufacturer_code": 4190
      },
      "endpoints": [
        {
          "id": 10,
          "profile_id": 260,
          "device_id": 256,
          "device_version": 1,
          "server_clusters": [
            {
              "id": 0,
              "manufacturer": false,
              "attributes": [
                {
                  "id": 57355,
                  "manufacturer": true,
                  "manufacturer_code": 4190,
                  "type": "string",
                  "writable": false,
                  "length": 64,
                  "default": "http://www.schneider-electric.com"
                },
                {
                  "id": 65533,
                  "manufacturer": false,
                  "type": "uint16",
                  "writable": false,
                  "default": 0
                }
              ],
              "commands": {
                "C->S": [
                  {
                    "id": 0,
                    "manufacturer": false
                  }
                ],
                "S->C": []
              }
            },
            {
              "id": 3,
              "manufacturer": false,
              "attributes": [
                {
                  "id": 0,
                  "manufacturer": false,
                  "type": "uint16",
                  "writable": true,
                  "default": 0
                },
                {
                  "id": 65533,
                  "manufacturer": false,
                  "type": "uint16",
                  "writable": true,
                  "default": 1
                }
              ],
              "commands": {
                "C->S": [
                  {
                    "id": 0,
                    "manufacturer": false
                  },
                  {
                    "id": 1,
                    "manufacturer": false
                  }
                ],
                "S->C": [
                  {
                    "id": 0,
                    "manufacturer": false
                  }
                ]
              }
            },
            {
              "id": 4,
              "manufacturer": false,
              "attributes": [
                {
                  "id": 0,
                  "manufacturer": false,
                  "type": "map8",
                  "writable": false,
                  "default": 0
                },
                {
                  "id": 65533,
                  "manufacturer": false,
                  "type": "uint16",
                  "writable": false,
                  "default": 0
                }
              ],
              "commands": {
                "C->S": [
                  {
                    "id": 0,
                    "manufacturer": false
                  },
                  {
                    "id": 1,
                    "manufacturer": false
                  },
                  {
                    "id": 2,
                    "manufacturer": false
                  },
                  {
                    "id": 3,
                    "manufacturer": false
                  },
                  {
                    "id": 4,
                    "manufacturer": false
                  },
                  {
                    "id": 5,
                    "manufacturer": false
                  }
                ],
                "S->C": [
                  {
                    "id": 0,
                    "manufacturer": false
                  },
                  {
                    "id": 1,
                    "manufacturer": false
                  },
                  {
                    "id": 2,
                    "manufacturer": false
                  },
                  {
                    "id": 3,
                    "manufacturer": false
                  }
                ]
              }
            },
            {
              "id": 5,
              "manufacturer": false,
              "attributes": [
                {
                  "id": 0,
                  "manufacturer": false,
                  "type": "uint8",
                  "writable": false,
                  "default": 0
                },
                {
                  "id": 1,
                  "manufacturer": false,
                  "type": "uint8",
                  "writable": false,
                  "default": 0
                },
                {
                  "id": 2,
                  "manufacturer": false,
                  "type": "uint16",
                  "writable": false,
                  "default": 0
                },
                {
                  "id": 3,
                  "manufacturer": false,
                  "type": "bool",
                  "writable": false,
                  "default": 0
                },
                {
                  "id": 4,
                  "manufacturer": false,
                  "type": "map8",
                  "writable": false,
                  "default": 0
                },
                {
                  "id": 65533,
                  "manufacturer": false,
                  "type": "uint16",
                  "writable": false,
                  "default": 0
                }
              ],
              "commands": {
                "C->S": [
                  {
                    "id": 0,
                    "manufacturer": false
                  },
                  {
                    "id": 1,
                    "manufacturer": false
                  },
                  {
                    "id": 2,
                    "manufacturer": false
                  },
                  {
                    "id": 3,
                    "manufacturer": false
                  },
                  {
                    "id": 4,
                    "manufacturer": false
                  },
                  {
                    "id": 5,
                    "manufacturer": false
                  },
                  {
                    "id": 6,
                    "manufacturer": false
                  }
                ],
                "S->C": []
              }
            },
            {
              "id": 6,
              "manufacturer": false,
              "attributes": [
                {
                  "id": 0,
                  "manufacturer": false,
                  "type": "bool",
                  "writable": false,
                  "default": 0
                },
                {
                  "id": 65533,
                  "manufacturer": false,
                  "type": "uint16",
                  "writable": false,
                  "default": 1
                }
              ],
              "commands": {
                "C->S": [
                  {
                    "id": 0,
                    "manufacturer": false
                  },
                  {
                    "id": 1,
                    "manufacturer": false
                  },
                  {
                    "id": 2,
                    "manufacturer": false
                  }
                ],
                "S->C": []
              }
            },
            {
              "id": 64516,
              "manufacturer": true,
              "manufacturer_code": 4190,
              "attributes": [
                {
                  "id": 0,
                  "manufacturer": true,
                  "manufacturer_code": 4190,
                  "type": "uint8",
                  "writable": true,
                  "default": 0
                },
                {
                  "id": 1,
                  "manufacturer": true,
                  "manufacturer_code": 4190,
                  "type": "uint8",
                  "writable": true,
                  "default": 0
                },
                {
                  "id": 2,
                  "manufacturer": true,
                  "manufacturer_code": 4190,
                  "type": "uint8",
                  "writable": true,
                  "default": 0
                },
                {
                  "id": 65533,
                  "manufacturer": true,
                  "manufacturer_code": 4190,
                  "type": "uint16",
                  "writable": true,
                  "default": 1
                }
              ],
              "commands": {}
            }
          ],
          "client_clusters": [
            {
              "id": 25,
              "manufacturer": false,
              "attributes": [
                {
                  "id": 0,
                  "manufacturer": false,
                  "type": "EUI64",
                  "writable": false,
                  "default": 0
                },
                {
                  "id": 1,
                  "manufacturer": false,
                  "type": "uint32",
                  "writable": false,
                  "default": 4294967295
                },
                {
                  "id": 2,
                  "manufacturer": false,
                  "type": "uint32",
                  "writable": false,
                  "default": 4294967295
                },
                {
                  "id": 3,
                  "manufacturer": false,
                  "type": "uint16",
                  "writable": false,
                  "default": 65535
                },
                {
                  "id": 4,
                  "manufacturer": false,
                  "type": "uint32",
                  "writable": false,
                  "default": 4294967295
                },
                {
                  "id": 5,
                  "manufacturer": false,
                  "type": "uint16",
                  "writable": false,
                  "default": 65535
                },
                {
                  "id": 6,
                  "manufacturer": false,
                  "type": "enum8",
                  "writable": false,
                  "default": 0
                },
                {
                  "id": 7,
                  "manufacturer": false,
                  "type": "uint16",
                  "writable": false,
                  "default": 0
                },
                {
                  "id": 8,
                  "manufacturer": false,
                  "type": "uint16",
                  "writable": false,
                  "default": 0
                },
                {
                  "id": 9,
                  "manufacturer": false,
                  "type": "uint16",
                  "writable": false,
                  "default": 0
                },
                {
                  "id": 10,
                  "manufacturer": false,
                  "type": "uint32",
                  "writable": false,
                  "default": 0
                },
                {
                  "id": 65533,
                  "manufacturer": false,
                  "type": "uint16",
                  "writable": false,
                  "default": 1
                }
              ],
              "commands": {
                "C->S": [
                  {
                    "id": 1,
                    "manufacturer": false
                  },
                  {
                    "id": 3,
                    "manufacturer": false
                  },
                  {
                    "id": 6,
                    "manufacturer": false
                  }
                ],
                "S->C": [
                  {
                    "id": 0,
                    "manufacturer": false
                  },
                  {
                    "id": 2,
                    "manufacturer": false
                  },
                  {
                    "id": 5,
                    "manufacturer": false
                  },
                  {
                    "id": 7,
                    "manufacturer": false
                  },
                  {
                    "id": 9,
                    "manufacturer": false
                  }
                ]
              }
            }
          ]
        }
      ]
    }
  }
}
```

> 记录不存在

```json
{
  "code": 10000,
  "data": {},
  "timestamp": 1654758360969,
  "uuid": "9e73867f-e7c2-11ec-aa03-1826492a4080",
  "message": "device 94DEB8FFFEF1343 not exist"
}
```

> 服务器内部错误

```json
{
  "code": 91000,
  "message": "no response",
  "timestamp": 1654758324807,
  "uuid": "88e5c413-e7c2-11ec-9f45-1826492a4080",
  "data": {}
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|记录不存在|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|服务器内部错误|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» message|string|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» data|object|true|none||none|
|»» config|object|true|none||none|
|»»» node|object|true|none||none|
|»»»» device_type|string|true|none||none|
|»»»» radio_power|integer|true|none||none|
|»»»» manufacturer_code|integer|true|none||none|
|»»» endpoints|[object]|true|none||none|
|»»»» id|integer|true|none||none|
|»»»» profile_id|integer|true|none||none|
|»»»» device_id|integer|true|none||none|
|»»»» device_version|integer|true|none||none|
|»»»» server_clusters|[object]|true|none||none|
|»»»»» id|integer|true|none||none|
|»»»»» manufacturer|boolean|true|none||none|
|»»»»» attributes|[object]|true|none||none|
|»»»»»» id|integer|true|none||none|
|»»»»»» manufacturer|boolean|true|none||none|
|»»»»»» manufacturer_code|integer|false|none||none|
|»»»»»» type|string|true|none||none|
|»»»»»» writable|boolean|true|none||none|
|»»»»»» length|integer|false|none||none|
|»»»»»» default|any|true|none||none|

*oneOf*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|»»»»»»» *anonymous*|string|false|none||none|

*xor*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|»»»»»»» *anonymous*|integer|false|none||none|

*continued*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|»»»»» commands|object|true|none||none|
|»»»»»» C->S|[object]|true|none||none|
|»»»»»»» id|integer|true|none||none|
|»»»»»»» manufacturer|boolean|true|none||none|
|»»»»»»» manufacturer_code|integer|false|none||none|
|»»»»»» S->C|[object]|true|none||none|
|»»»»»»» id|integer|true|none||none|
|»»»»»»» manufacturer|boolean|true|none||none|
|»»»»»»» manufacturer_code|integer|false|none||none|
|»»»»» manufacturer_code|integer|false|none||none|
|»»»» client_clusters|[object]|true|none||none|
|»»»»» id|integer|true|none||none|
|»»»»» manufacturer|boolean|true|none||none|
|»»»»» manufacturer_code|integer|false|none||none|
|»»»»» attributes|[object]|false|none||none|
|»»»»»» id|integer|true|none||none|
|»»»»»» manufacturer|boolean|true|none||none|
|»»»»»» manufacturer_code|integer|false|none||none|
|»»»»»» type|string|true|none||none|
|»»»»»» length|integer|false|none||none|
|»»»»»» writable|boolean|true|none||none|
|»»»»»» default|any|true|none||none|

*oneOf*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|»»»»»»» *anonymous*|string|false|none||none|

*xor*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|»»»»»»» *anonymous*|integer|false|none||none|

*continued*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|»»»»» commands|object|false|none||none|
|»»»»»» C->S|[object]|true|none||none|
|»»»»»»» id|integer|true|none||none|
|»»»»»»» manufacturer|boolean|true|none||none|
|»»»»»»» manufacturer_code|integer|false|none||none|
|»»»»»» S->C|[object]|true|none||none|
|»»»»»»» id|integer|true|none||none|
|»»»»»»» manufacturer|boolean|true|none||none|
|»»»»»»» manufacturer_code|integer|false|none||none|

状态码 **404**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **500**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## POST 使用配置文件更新设备配置

POST /devices/{mac}/config

> Body 请求参数

```yaml
file: string

```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|mac|path|string| 是 |none|
|body|body|object| 否 |none|
|» file|body|string(binary)| 是 |none|

> 返回示例

> 200 Response

```json
{
  "code": 0,
  "data": {},
  "timestamp": 0,
  "uuid": "string",
  "message": "string"
}
```

> 记录不存在

```json
{
  "code": 10000,
  "data": {},
  "timestamp": 1654759454855,
  "uuid": "2a7554b7-e7c5-11ec-89bf-1826492a4080",
  "message": "device 1234 not exist"
}
```

> 服务器内部错误

```json
{
  "code": 91000,
  "message": "no response",
  "timestamp": 1654759720468,
  "uuid": "c8c6b2fb-e7c5-11ec-879f-1826492a4080",
  "data": {}
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|记录不存在|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|服务器内部错误|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **404**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **500**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

# api/2/Simulators

## GET 获取全部simulators

GET /simulators

> 返回示例

> 成功

```json
{
  "code": 0,
  "data": [
    {
      "ip": "192.168.121.51",
      "mac": "18:26:49:2a:40:80",
      "name": "simulator-192.168.121.51",
      "version": "1.2.3",
      "connected": true,
      "label": "",
      "devices": [
        "94DEB8FFFEEE462C",
        "94DEB8FFFEEE4C05",
        "94DEB8FFFEF6DBD4",
        "94DEB8FFFEEE4599",
        "94DEB8FFFEF13008",
        "94DEB8FFFEF6E634",
        "94DEB8FFFEF12384",
        "94DEB8FFFEEE4CE6",
        "94DEB8FFFEF12436",
        "94DEB8FFFEF11851",
        "94DEB8FFFEF117E8",
        "94DEB8FFFEF123B1",
        "94DEB8FFFEF12BB5",
        "94DEB8FFFEEE461D",
        "94DEB8FFFEF6DAE9",
        "94DEB8FFFEF126E7",
        "94DEB8FFFEF12ABF",
        "94DEB8FFFEF1343C"
      ]
    }
  ],
  "timestamp": 1654046128594,
  "uuid": "52dfedd9-e148-11ec-8316-1826492a4080",
  "message": ""
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|[object]|true|none||none|
|»» ip|string|true|none||IP address|
|»» mac|string|true|none||MAC address|
|»» name|string|true|none||Name|
|»» version|string|true|none||Version|
|»» connected|boolean|true|none||Connected state|
|»» label|string|true|none||User label|
|»» devices|[string]|true|none||Devices list|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## GET 按照MAC地址获取一个simulator

GET /simulators/{mac}

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|mac|path|string| 是 |Simulator Ethernet Mac address|

> 返回示例

> 成功

```json
{
  "code": 0,
  "data": {
    "ip": "192.168.121.51",
    "mac": "18:26:49:2a:40:80",
    "name": "simulator-192.168.121.51",
    "version": "1.2.3",
    "connected": true,
    "label": "",
    "devices": [
      "94DEB8FFFEEE462C",
      "94DEB8FFFEEE4C05",
      "94DEB8FFFEF6DBD4",
      "94DEB8FFFEEE4599",
      "94DEB8FFFEF13008",
      "94DEB8FFFEF6E634",
      "94DEB8FFFEF12384",
      "94DEB8FFFEEE4CE6",
      "94DEB8FFFEF12436",
      "94DEB8FFFEF11851",
      "94DEB8FFFEF117E8",
      "94DEB8FFFEF123B1",
      "94DEB8FFFEF12BB5",
      "94DEB8FFFEEE461D",
      "94DEB8FFFEF6DAE9",
      "94DEB8FFFEF126E7",
      "94DEB8FFFEF12ABF",
      "94DEB8FFFEF1343C"
    ]
  },
  "timestamp": 1654046363008,
  "uuid": "de9897ab-e148-11ec-984a-1826492a4080",
  "message": ""
}
```

> 记录不存在

```json
{
  "code": 20000,
  "data": {},
  "timestamp": 1654046377840,
  "uuid": "e76fc1a2-e148-11ec-b0e3-1826492a4080",
  "message": "simulator 18:26:49:2a:40:81 not exist"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|记录不存在|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|»» ip|string|true|none||none|
|»» mac|string|true|none||none|
|»» name|string|true|none||none|
|»» version|string|true|none||none|
|»» connected|boolean|true|none||none|
|»» label|string|true|none||none|
|»» devices|[string]|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **404**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## PUT 修改simulator label信息

PUT /simulators/{mac}

> Body 请求参数

```json
{
  "label": {
    "data": "string"
  }
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|mac|path|string| 是 |none|
|body|body|object| 否 |none|
|» label|body|object| 是 |label command|
|»» data|body|string| 是 |none|

> 返回示例

> 成功

```json
{
  "code": 0,
  "message": "",
  "data": {}
}
```

> 记录不存在

```json
{
  "code": 20000,
  "message": "simulator 18:26:49:2a:40:80 not exist",
  "data": {}
}
```

> 服务器错误

```json
{
  "code": 20001,
  "message": "simulator 18:26:49:2a:40:80 is offline",
  "data": {}
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|记录不存在|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|服务器错误|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» message|string|true|none||none|
|» data|object|true|none||none|

状态码 **404**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» message|string|true|none||none|
|» data|object|true|none||none|

状态码 **500**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» message|string|true|none||none|
|» data|object|true|none||none|

# api/2/Firmwares

## GET 获取固件列表

GET /firmwares

获取后台保存的固件列表

> 返回示例

> 成功

```json
{
  "code": 0,
  "data": [
    "WiserZigbeeLauncherTestHarnessV0.0.1.gbl",
    "WiserZigbeeLauncherTestHarnessV9.0.1.gbl",
    "WiserZLTH-PuckSwitch-V0.1.3.gbl",
    "WiserZLTH-TemHum-V0.0.3.gbl"
  ],
  "timestamp": 1654060718008,
  "uuid": "4ad7b248-e16a-11ec-b528-1826492a4080",
  "message": ""
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|[string]|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## POST 上传固件

POST /firmwares

上传固件到固件列表

> Body 请求参数

```yaml
file: string

```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|object| 否 |none|
|» file|body|string(binary)| 是 |firmware file|

> 返回示例

> 成功

```json
{
  "code": 0,
  "data": {},
  "timestamp": 1654060932179,
  "uuid": "ca7fa985-e16a-11ec-8cb0-1826492a4080",
  "message": ""
}
```

> 服务器错误

```json
{
  "code": 90000,
  "data": {},
  "timestamp": 1654061208295,
  "uuid": "6f13a5e7-e16b-11ec-98f4-1826492a4080",
  "message": "internal error: file not found"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|服务器错误|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **500**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## PUT 更新指定设备的固件

PUT /firmwares

批量更新Device固件

> Body 请求参数

```json
{
  "filename": "WiserZLTH-PuckSwitch-V0.1.3.gbl",
  "devices": [
    "94DEB8FFFEF12ABF"
  ]
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|object| 否 |none|
|» filename|body|string| 是 |firmware filename|
|» devices|body|[string]| 是 |device list|

> 返回示例

> 成功

```json
{
  "code": 0,
  "message": "",
  "timestamp": 1654061389389,
  "uuid": "db0467c6-e16b-11ec-b693-1826492a4080",
  "data": {}
}
```

> 服务器错误

```json
{
  "code": 10000,
  "data": {},
  "timestamp": 1654061589728,
  "uuid": "526dc08d-e16c-11ec-9dac-1826492a4080",
  "message": "device 94DEB8FFFEF112D not exist"
}
```

```json
{
  "code": 10001,
  "data": {},
  "timestamp": 1654061617841,
  "uuid": "632f61ea-e16c-11ec-a59f-1826492a4080",
  "message": "device 94DEB8FFFEF112DA is offline"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|服务器错误|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» message|string|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» data|object|true|none||none|

状态码 **500**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## DELETE 删除指定的固件

DELETE /firmwares

> Body 请求参数

```json
{
  "filename": "WiserZLTH_CFG_V1.0.1.gbl"
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|object| 否 |none|
|» filename|body|string| 是 |none|

> 返回示例

> 成功

```json
{
  "code": 0,
  "data": {},
  "timestamp": 1655886397835,
  "uuid": "08d18293-f205-11ec-a406-1826492a4080",
  "message": ""
}
```

> 服务器内部错误

```json
{
  "code": 50000,
  "data": {},
  "timestamp": 1655886413694,
  "uuid": "124579c7-f205-11ec-87f8-1826492a4080",
  "message": "file WiserZLTH_CFG_V1.0.1.gbl not exist"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|服务器内部错误|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **500**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

# api/2/Zigbees

## GET 获取全部设备Zigbee信息

GET /zigbees

> 返回示例

> 成功

```json
{
  "code": 0,
  "data": [
    {
      "mac": "94DEB8FFFEF112DA",
      "node_id": "FFFE",
      "device_type": "unknown",
      "extended_pan_id": "0000000000000000",
      "channel": 255,
      "id": 1,
      "pan_id": "FFFF"
    }
  ],
  "timestamp": 1654062428100,
  "uuid": "46232952-e16e-11ec-95e8-1826492a4080",
  "message": ""
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||error code|
|» message|string|true|none||error description|
|» timestamp|integer|true|none||request timestamp|
|» uuid|string|true|none||request uuid|
|» data|[object]|true|none||response data|
|»» extended_pan_id|integer|true|none||network extended PAN id|
|»» device_type|string|true|none||device type|
|»» pan_id|integer|true|none||network PAN ID|
|»» channel|integer|true|none||network channel|
|»» node_id|integer|true|none||network node ID|
|»» mac|string|true|none||zigbee mac address|

## GET 按照MAC地址获取设备Zigbee信息

GET /zigbees/{mac}

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|mac|path|string| 是 |zigbee mac address|

> 返回示例

> 成功

```json
{
  "code": 0,
  "data": {
    "mac": "94DEB8FFFEF11F35",
    "pan_id": 65535,
    "node_id": 65534,
    "channel": 255,
    "device_type": "unknown",
    "extended_pan_id": 0
  },
  "timestamp": 1655777473761,
  "uuid": "6d02ca31-f107-11ec-ac72-1826492a4080",
  "message": ""
}
```

> 记录不存在

```json
{
  "code": 10000,
  "data": {},
  "timestamp": 1654063215696,
  "uuid": "1b94beba-e170-11ec-ae78-1826492a4080",
  "message": "device 94DEB8FFFEF12AB not exist"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|记录不存在|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|»» pan_id|integer|true|none||none|
|»» channel|integer|true|none||none|
|»» node_id|integer|true|none||none|
|»» mac|string|true|none||none|
|»» extended_pan_id|integer|true|none||none|
|»» device_type|string|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **404**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## PUT 修改device的zigbee属性

PUT /zigbees/{mac}

该接口支持修改设备zigbee属性值，触发设备入网，离网，触发sleepy end device设备发出data request命令

> Body 请求参数

```json
{
  "join": {
    "channels": [
      11,
      12
    ],
    "extended_pan_id": 51,
    "pan_id": 85
  },
  "leave": {},
  "data_request": {},
  "attribute": {
    "endpoint": 77,
    "cluster": 28,
    "server": false,
    "manufacturer": true,
    "attribute": 49,
    "type": "uint8",
    "value": 15,
    "manufacturer_code": 45
  }
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|mac|path|string| 是 |zigbee mac address|
|body|body|object| 否 |none|
|» join|body|object| 否 |join command, trigger device joining to a specific zigbee network|
|»» channels|body|[integer]| 是 |network channels, 11,12,13, ..., 26|
|»» pan_id|body|integer| 否 |network PAN ID, 2 bytes, set this property if 'auto_option' is 0 or 2,|
|»» extended_pan_id|body|integer| 否 |network extended PAN ID, 8 bytes, set this property if 'auto_option' is 0 or 1|
|» leave|body|object| 否 |leave command, trigger device leaving to current zigbee network|
|» data_request|body|object| 否 |data request command, trigger sleepy end device send out data_request_command|
|» attribute|body|object| 否 |change attribute value|
|»» endpoint|body|integer| 是 |endpoint id, rang 1-240|
|»» cluster|body|integer| 是 |cluster ID, range 0-65535|
|»» server|body|boolean| 是 |server cluster mask|
|»» manufacturer|body|boolean| 是 |manufacturer specific mask fro this cluster|
|»» manufacturer_code|body|integer| 否 |manufacturer code for this cluster if cluster_manufacturer is true, range 0-65535|
|»» attribute|body|integer| 是 |attribute ID, range 0-65535|
|»» type|body|string| 是 |attribute type|
|»» value|body|any| 是 |attribute value, could be integer or string|
|»»» *anonymous*|body|integer| 否 |integer data|
|»»» *anonymous*|body|string| 否 |string data|

> 返回示例

> 成功

```json
{
  "code": 0,
  "message": "",
  "timestamp": 1654063999654,
  "uuid": "eedb3282-e171-11ec-865a-1826492a4080",
  "data": {}
}
```

> 记录不存在

```json
{
  "code": 10000,
  "data": {},
  "timestamp": 1654064037605,
  "uuid": "057a2375-e172-11ec-bb9d-1826492a4080",
  "message": "device 94DEB8FFFEF12AB not exist"
}
```

> 服务器内部错误

```json
{
  "code": 10001,
  "data": {},
  "timestamp": 1654064285247,
  "uuid": "99154351-e172-11ec-8cd7-1826492a4080",
  "message": "device 94DEB8FFFEF112DA is offline"
}
```

```json
{
  "code": 10002,
  "data": {},
  "timestamp": 1654064433434,
  "uuid": "f168b477-e172-11ec-a2e9-1826492a4080",
  "message": "device 94DEB8FFFEF112DA is in bootloader or upgrading mode"
}
```

```json
{
  "code": 90008,
  "message": "no response",
  "data": {},
  "timestamp": 1653630453988,
  "uuid": "81808529-dd80-11ec-840b-1826492a4080"
}
```

```json
{
  "code": 40001,
  "data": {},
  "timestamp": 1654064327706,
  "uuid": "b263f0ba-e172-11ec-ba59-1826492a4080",
  "message": "94DEB8FFFEEE57A9 already in a network"
}
```

```json
{
  "code": 40000,
  "data": {},
  "timestamp": 1654064327706,
  "uuid": "b263f0ba-e172-11ec-ba59-1826492a4080",
  "message": "94DEB8FFFEEE57A9 not in any network"
}
```

```json
{
  "code": 90004,
  "data": {},
  "timestamp": 1654071247721,
  "uuid": "cf0a7354-e182-11ec-9069-1826492a4080",
  "message": "json validation failed:'data' is a required property"
}
```

```json
{
  "code": 90002,
  "data": {},
  "timestamp": 1654071175835,
  "uuid": "a4317637-e182-11ec-8762-1826492a4080",
  "message": "unsupported command: identifyii"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|记录不存在|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|服务器内部错误|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» message|string|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» data|object|true|none||none|

状态码 **404**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **500**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## GET 获取设备zigbee属性信息

GET /zigbees/{mac}/attributes

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|mac|path|string| 是 |none|
|endpoint|query|integer| 是 |none|
|cluster|query|integer| 是 |none|
|server|query|integer| 是 |none|
|attribute|query|integer| 是 |none|
|manufacturer|query|integer| 是 |none|
|manufacturer_code|query|integer| 否 |none|

> 返回示例

> 成功

```json
{
  "code": 0,
  "message": "",
  "timestamp": 1655276094375,
  "uuid": "0f9bd8da-ec78-11ec-b6df-1826492a4080",
  "data": {
    "endpoint": 1,
    "cluster": 6,
    "server": true,
    "attribute": 0,
    "manufacturer": false,
    "manufacturer_code": 0,
    "type": "bool",
    "value": 0
  }
}
```

> 记录不存在

```json
{
  "code": 10000,
  "data": {},
  "timestamp": 1654146955048,
  "uuid": "141fb884-e233-11ec-9a40-1826492a4080",
  "message": "device 94DEB8FFFEF11DFA not exist"
}
```

> 服务器内部错误

```json
{
  "code": 6,
  "message": "please refer error code specification",
  "timestamp": 1654146994186,
  "uuid": "2b73d2db-e233-11ec-b6f3-1826492a4080",
  "data": {}
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|记录不存在|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|服务器内部错误|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» message|string|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» data|object|true|none||none|
|»» endpoint|integer|true|none||none|
|»» cluster|integer|true|none||none|
|»» server|boolean|true|none||none|
|»» attribute|integer|true|none||none|
|»» manufacturer|boolean|true|none||none|
|»» manufacturer_code|integer|false|none||none|
|»» type|string|true|none||none|
|»» length|integer|false|none||none|
|»» value|any|true|none||none|

*oneOf*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|»»» *anonymous*|string|false|none||none|

*xor*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|»»» *anonymous*|integer|false|none||none|

状态码 **404**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **500**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

# api/2/configs

## GET 获取config模板文件列表

GET /configs/files

> 返回示例

> 成功

```json
{
  "code": 0,
  "data": [
    {
      "filename": "1G_Switch.yml",
      "device_type": "router",
      "endpoints": [
        {
          "id": 10,
          "device_id": 256,
          "profile_id": 260,
          "server_clusters": [
            0,
            3,
            4,
            5,
            6,
            64516
          ],
          "client_clusters": [
            25
          ]
        }
      ]
    },
    {
      "filename": "1G_Switch_new.yml",
      "device_type": "router",
      "endpoints": [
        {
          "id": 10,
          "device_id": 256,
          "profile_id": 260,
          "server_clusters": [
            0,
            3,
            4,
            5,
            6,
            64516
          ],
          "client_clusters": [
            25
          ]
        }
      ]
    },
    {
      "filename": "2G_Switch.yml",
      "device_type": "router",
      "endpoints": [
        {
          "id": 10,
          "device_id": 256,
          "profile_id": 260,
          "server_clusters": [
            0,
            3,
            4,
            5,
            6,
            64516
          ],
          "client_clusters": [
            25
          ]
        },
        {
          "id": 11,
          "device_id": 256,
          "profile_id": 260,
          "server_clusters": [
            0,
            3,
            4,
            5,
            6,
            64516
          ],
          "client_clusters": [
            25
          ]
        }
      ]
    }
  ],
  "timestamp": 1654752849896,
  "uuid": "c9988670-e7b5-11ec-9a03-1826492a4080",
  "message": ""
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|[object]|true|none||none|
|»» filename|string|true|none||none|
|»» device_type|string|true|none||none|
|»» endpoints|[object]|true|none||none|
|»»» id|integer|true|none||none|
|»»» device_id|integer|true|none||none|
|»»» profile_id|integer|true|none||none|
|»»» server_clusters|[integer]|true|none||none|
|»»» client_clusters|[integer]|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## DELETE 删除全部模板文件

DELETE /configs/files

> 返回示例

> 成功

```json
{
  "code": 0,
  "data": {},
  "timestamp": 1654752654868,
  "uuid": "5559a6b6-e7b5-11ec-8525-1826492a4080",
  "message": ""
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## POST 上传模板文件

POST /configs/files

> Body 请求参数

```yaml
file: file://D:\projects\zigbee_launcher\development\files\hello.ymlnew

```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|object| 否 |none|
|» file|body|string(binary)| 是 |none|

> 返回示例

> 成功

```json
{
  "code": 0,
  "data": {},
  "timestamp": 1654746342252,
  "uuid": "a2bcec2b-e7a6-11ec-a523-1826492a4080",
  "message": ""
}
```

> 服务器内部错误

```json
{
  "code": 90004,
  "data": {},
  "timestamp": 1654752326223,
  "uuid": "91766b43-e7b4-11ec-8230-1826492a4080",
  "message": "json validation failed:'name' is a required property"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|服务器内部错误|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **500**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## GET 获取一个config模板文件内容

GET /configs/files/{filename}

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|filename|path|string| 是 |none|

> 返回示例

> 成功

```json
{
  "code": 0,
  "data": {
    "filename": "template.yml",
    "config": {
      "endpoints": [
        {
          "client_clusters": [
            {
              "attributes": [
                {
                  "default": "8",
                  "id": 0,
                  "length": 1,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "ZCL Version",
                  "type": "uint8",
                  "writable": false
                },
                {
                  "default": "0",
                  "id": 1,
                  "length": 1,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Application Version",
                  "type": "uint8",
                  "writable": false
                },
                {
                  "default": "0",
                  "id": 2,
                  "length": 1,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Stack Version",
                  "type": "uint8",
                  "writable": false
                },
                {
                  "default": "0",
                  "id": 3,
                  "length": 1,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "HW Version",
                  "type": "uint8",
                  "writable": false
                },
                {
                  "default": "",
                  "id": 4,
                  "length": 32,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Manufacturer Name",
                  "type": "string",
                  "writable": false
                },
                {
                  "default": "",
                  "id": 5,
                  "length": 32,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Model Identifier",
                  "type": "string",
                  "writable": false
                },
                {
                  "default": "",
                  "id": 6,
                  "length": 16,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Data Code",
                  "type": "string",
                  "writable": false
                },
                {
                  "default": "0",
                  "id": 7,
                  "length": 1,
                  "manufacturer": true,
                  "manufacturer_code": 1234,
                  "name": "Power Source",
                  "type": "enum8",
                  "writable": false
                }
              ],
              "commands": {
                "S->C": [],
                "C->S": [
                  {
                    "description": "Reset to Factory Defaults",
                    "id": 0,
                    "manufacturer": true,
                    "manufacturer_code": 1234
                  }
                ]
              },
              "id": 0,
              "manufacturer": false,
              "manufacturer_code": 0,
              "name": "Basic,"
            },
            {
              "attributes": [
                {
                  "default": "0",
                  "id": 0,
                  "length": 2,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Mains Voltage",
                  "type": "uint16",
                  "writable": false
                },
                {
                  "default": "0",
                  "id": 1,
                  "length": 1,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Mains Frequency",
                  "type": "uint8",
                  "writable": false
                }
              ],
              "commands": {
                "C->S": [],
                "S->C": []
              },
              "id": 1,
              "manufacturer": false,
              "manufacturer_code": 0,
              "name": "Power Configuration"
            },
            {
              "attributes": [
                {
                  "default": "0",
                  "id": 0,
                  "length": 1,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Name Support",
                  "type": "map8",
                  "writable": false
                }
              ],
              "commands": {
                "S->C": [
                  {
                    "description": "Add group response",
                    "id": 0,
                    "manufacturer": false,
                    "manufacturer_code": 0
                  },
                  {
                    "description": "View group response",
                    "id": 1,
                    "manufacturer": false,
                    "manufacturer_code": 0
                  }
                ],
                "C->S": [
                  {
                    "description": "Add group",
                    "id": 0,
                    "manufacturer": false,
                    "manufacturer_code": 0
                  },
                  {
                    "description": "View group",
                    "id": 1,
                    "manufacturer": false,
                    "manufacturer_code": 0
                  }
                ]
              },
              "id": 4,
              "manufacturer": false,
              "manufacturer_code": 0,
              "name": "Groups"
            }
          ],
          "device_id": 1,
          "device_version": 1,
          "id": 1,
          "profile_id": 1,
          "server_clusters": [
            {
              "attributes": [
                {
                  "default": "",
                  "id": 0,
                  "length": 1,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "ZCL Version",
                  "type": "uint8",
                  "writable": false
                },
                {
                  "default": "",
                  "id": 1,
                  "length": 1,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Application Version",
                  "type": "uint8",
                  "writable": false
                },
                {
                  "default": "",
                  "id": 2,
                  "length": 1,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Stack Version",
                  "type": "uint8",
                  "writable": false
                },
                {
                  "default": "",
                  "id": 3,
                  "length": 1,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "HW Version",
                  "type": "uint8",
                  "writable": false
                },
                {
                  "default": "",
                  "id": 4,
                  "length": 32,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Manufacturer Name",
                  "type": "string",
                  "writable": false
                },
                {
                  "default": "",
                  "id": 5,
                  "length": 32,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Model Identifier",
                  "type": "string",
                  "writable": false
                },
                {
                  "default": "",
                  "id": 6,
                  "length": 16,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Data Code",
                  "type": "string",
                  "writable": false
                },
                {
                  "default": "0",
                  "id": 7,
                  "length": 1,
                  "manufacturer": true,
                  "manufacturer_code": 1234,
                  "name": "Power Source",
                  "type": "enum8",
                  "writable": false
                }
              ],
              "commands": {
                "S->C": [],
                "C->S": [
                  {
                    "description": "Reset to Factory Defaults",
                    "id": 0,
                    "manufacturer": true,
                    "manufacturer_code": 1234
                  }
                ]
              },
              "id": 0,
              "manufacturer": false,
              "manufacturer_code": 0,
              "name": "Basic,"
            },
            {
              "attributes": [
                {
                  "default": "",
                  "id": 0,
                  "length": 2,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Mains Voltage",
                  "type": "uint16",
                  "writable": false
                },
                {
                  "default": "0",
                  "id": 1,
                  "length": 1,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Mains Frequency",
                  "type": "uint8",
                  "writable": false
                }
              ],
              "commands": {
                "C->S": [],
                "S->C": []
              },
              "id": 1,
              "manufacturer": false,
              "manufacturer_code": 0,
              "name": "Power Configuration"
            },
            {
              "attributes": [
                {
                  "default": "0",
                  "id": 0,
                  "length": 1,
                  "manufacturer": false,
                  "manufacturer_code": 0,
                  "name": "Name Support",
                  "type": "map8",
                  "writable": false
                }
              ],
              "commands": {
                "S->C": [
                  {
                    "description": "Add group response",
                    "id": 0,
                    "manufacturer": false,
                    "manufacturer_code": 0
                  },
                  {
                    "description": "View group response",
                    "id": 1,
                    "manufacturer": false,
                    "manufacturer_code": 0
                  }
                ],
                "C->S": [
                  {
                    "description": "Add group",
                    "id": 0,
                    "manufacturer": false,
                    "manufacturer_code": 0
                  },
                  {
                    "description": "View group",
                    "id": 1,
                    "manufacturer": false,
                    "manufacturer_code": 0
                  }
                ]
              },
              "id": 4,
              "manufacturer": false,
              "manufacturer_code": 0,
              "name": "Groups"
            }
          ]
        }
      ],
      "node": {
        "device_type": "router",
        "manufacturer_code": 1234,
        "radio_power": 10
      }
    }
  },
  "timestamp": 1654737173955,
  "uuid": "4a01db49-e791-11ec-8147-1826492a4080",
  "message": ""
}
```

> 500 Response

```json
{
  "code": 0,
  "data": {},
  "timestamp": 0,
  "uuid": "string",
  "message": "string"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|服务器内部错误|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|»» filename|string|true|none||none|
|»» config|object|true|none||none|
|»»» endpoints|[object]|true|none||none|
|»»»» client_clusters|[object]|false|none||none|
|»»»»» attributes|[object]|true|none||none|
|»»»»»» default|any|true|none||none|

*oneOf*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|»»»»»»» *anonymous*|string|false|none||none|

*xor*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|»»»»»»» *anonymous*|integer|false|none||none|

*continued*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|»»»»»» id|integer|true|none||none|
|»»»»»» length|integer|false|none||none|
|»»»»»» manufacturer|boolean|true|none||none|
|»»»»»» manufacturer_code|integer|false|none||none|
|»»»»»» name|string|true|none||none|
|»»»»»» type|string|true|none||none|
|»»»»»» writable|boolean|true|none||none|
|»»»»» commands|object|true|none||none|
|»»»»»» S->C|[object]|true|none||none|
|»»»»»»» description|string|true|none||none|
|»»»»»»» id|integer|true|none||none|
|»»»»»»» manufacturer|boolean|true|none||none|
|»»»»»»» manufacturer_code|integer|false|none||none|
|»»»»»» C->S|[object]|true|none||none|
|»»»»»»» description|string|true|none||none|
|»»»»»»» id|integer|true|none||none|
|»»»»»»» manufacturer|boolean|true|none||none|
|»»»»»»» manufacturer_code|integer|false|none||none|
|»»»»» id|integer|true|none||none|
|»»»»» manufacturer|boolean|true|none||none|
|»»»»» manufacturer_code|integer|false|none||none|
|»»»»» name|string|true|none||none|
|»»»» device_id|integer|false|none||none|
|»»»» device_version|integer|false|none||none|
|»»»» id|integer|false|none||none|
|»»»» profile_id|integer|false|none||none|
|»»»» server_clusters|[object]|false|none||none|
|»»»»» attributes|[object]|true|none||none|
|»»»»»» default|any|true|none||none|

*oneOf*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|»»»»»»» *anonymous*|string|false|none||none|

*xor*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|»»»»»»» *anonymous*|integer|false|none||none|

*continued*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|»»»»»» id|integer|true|none||none|
|»»»»»» length|integer|false|none||none|
|»»»»»» manufacturer|boolean|true|none||none|
|»»»»»» manufacturer_code|integer|false|none||none|
|»»»»»» name|string|true|none||none|
|»»»»»» type|string|true|none||none|
|»»»»»» writable|boolean|true|none||none|
|»»»»» commands|object|true|none||none|
|»»»»»» S->C|[object]|true|none||none|
|»»»»»»» description|string|true|none||none|
|»»»»»»» id|integer|true|none||none|
|»»»»»»» manufacturer|boolean|true|none||none|
|»»»»»»» manufacturer_code|integer|false|none||none|
|»»»»»» C->S|[object]|true|none||none|
|»»»»»»» description|string|true|none||none|
|»»»»»»» id|integer|true|none||none|
|»»»»»»» manufacturer|boolean|true|none||none|
|»»»»»»» manufacturer_code|integer|false|none||none|
|»»»»» id|integer|true|none||none|
|»»»»» manufacturer|boolean|true|none||none|
|»»»»» manufacturer_code|integer|false|none||none|
|»»»»» name|string|true|none||none|
|»»» node|object|true|none||none|
|»»»» device_type|string|true|none||none|
|»»»» manufacturer_code|integer|true|none||none|
|»»»» radio_power|integer|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **500**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## DELETE 删除一个config模板文件

DELETE /configs/files/{filename}

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|filename|path|string| 是 |none|

> 返回示例

> 成功

```json
{
  "code": 0,
  "data": {},
  "timestamp": 1654753301746,
  "uuid": "d6eb6aa7-e7b6-11ec-a7c1-1826492a4080",
  "message": ""
}
```

> 500 Response

```json
{
  "code": 0,
  "data": {},
  "timestamp": 0,
  "uuid": "string",
  "message": "string"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|服务器内部错误|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **500**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## POST 保存config模板

POST /configs

> Body 请求参数

```json
{
  "filename": "1G_Switch.yml",
  "config": {
    "endpoints": [
      {
        "client_clusters": [
          {
            "id": 25,
            "name": "Over-The-Air Upgrade",
            "manufacturer": false,
            "attributes": [
              {
                "id": 0,
                "name": "UpgradeServerID",
                "type": "EUI64",
                "writable": false,
                "default": 18446744073709552000,
                "manufacturer": false
              },
              {
                "id": 1,
                "name": "FileOffset",
                "type": "uint32",
                "writable": false,
                "default": 4294967295,
                "manufacturer": false
              },
              {
                "id": 2,
                "name": "CurrentFileVersion",
                "type": "uint32",
                "writable": false,
                "default": 4294967295,
                "manufacturer": false
              },
              {
                "id": 3,
                "name": "CurrentZigBeeStackVersion",
                "type": "uint16",
                "writable": false,
                "default": 65535,
                "manufacturer": false
              },
              {
                "id": 4,
                "name": "DownloadedFileVersion",
                "type": "uint32",
                "writable": false,
                "default": 4294967295,
                "manufacturer": false
              },
              {
                "id": 5,
                "name": "DownloadedZigBeeStackVersion",
                "type": "uint16",
                "writable": false,
                "default": 65535,
                "manufacturer": false
              },
              {
                "id": 6,
                "name": "ImageUpgradeStatus",
                "type": "enum8",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 7,
                "name": "ManufacturerID",
                "type": "uint16",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 8,
                "name": "ImageTypeID",
                "type": "uint16",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 9,
                "name": "MinimumBlockPeriod",
                "type": "uint16",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 10,
                "name": "ImageStamp",
                "type": "uint32",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 65533,
                "name": "ClusterRevision",
                "type": "uint16",
                "writable": false,
                "default": 1,
                "manufacturer": false
              }
            ],
            "commands": {
              "C->S": [
                {
                  "id": 1,
                  "description": "Query Next Image Request",
                  "manufacturer": false
                },
                {
                  "id": 3,
                  "description": "Image Block Request",
                  "manufacturer": false
                },
                {
                  "id": 6,
                  "description": "Upgrade End Request",
                  "manufacturer": false
                }
              ],
              "S->C": [
                {
                  "id": 0,
                  "description": "Image Notify",
                  "manufacturer": false
                },
                {
                  "id": 2,
                  "description": "Query Next Image Response",
                  "manufacturer": false
                },
                {
                  "id": 5,
                  "description": "Image Block Response",
                  "manufacturer": false
                },
                {
                  "id": 7,
                  "description": "Upgrade End Response",
                  "manufacturer": false
                },
                {
                  "id": 9,
                  "description": "Query Device Specific File Response",
                  "manufacturer": false
                }
              ]
            }
          }
        ],
        "device_id": 256,
        "device_version": 1,
        "id": 10,
        "profile_id": 260,
        "server_clusters": [
          {
            "id": 0,
            "name": "Basic",
            "manufacturer": false,
            "attributes": [
              {
                "id": 0,
                "name": "ZCLVersion",
                "type": "uint8",
                "writable": false,
                "default": 2,
                "manufacturer": false
              },
              {
                "id": 1,
                "name": "ApplicationVersion",
                "type": "uint8",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 2,
                "name": "StackVersion",
                "type": "uint8",
                "writable": false,
                "default": 2,
                "manufacturer": false
              },
              {
                "id": 3,
                "name": "HWVersion",
                "type": "uint8",
                "writable": false,
                "default": 1,
                "manufacturer": false
              },
              {
                "id": 4,
                "name": "ManufacturerName",
                "type": "string",
                "length": 32,
                "writable": false,
                "default": "Schneider Electric",
                "manufacturer": false
              },
              {
                "id": 5,
                "name": "ModelIdentifier",
                "type": "string",
                "length": 32,
                "writable": false,
                "default": "E8331SRY800ZB",
                "manufacturer": false
              },
              {
                "id": 6,
                "name": "DataCode",
                "type": "string",
                "length": 16,
                "writable": false,
                "default": "",
                "manufacturer": false
              },
              {
                "id": 7,
                "name": "PowerSource",
                "type": "enum8",
                "writable": false,
                "default": 1,
                "manufacturer": false
              },
              {
                "id": 10,
                "name": "ProductCode",
                "type": "octstr",
                "length": 16,
                "writable": false,
                "default": "",
                "manufacturer": false
              },
              {
                "id": 16384,
                "name": "SWBuildID",
                "type": "string",
                "length": 16,
                "writable": false,
                "default": "",
                "manufacturer": false
              },
              {
                "id": 57345,
                "name": "SoftwareVersionString",
                "type": "string",
                "length": 20,
                "writable": false,
                "default": "1.1.1",
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 57346,
                "name": "HardwareVersionString",
                "type": "string",
                "length": 20,
                "writable": false,
                "default": "1.1.1",
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 57348,
                "name": "SerialNumber",
                "type": "string",
                "length": 32,
                "writable": false,
                "default": "",
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 57351,
                "name": "ProductIdentifier",
                "type": "enum16",
                "writable": false,
                "default": 0,
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 57352,
                "name": "ProductRange",
                "type": "string",
                "length": 16,
                "writable": false,
                "default": "",
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 57353,
                "name": "ProductModel",
                "type": "string",
                "length": 16,
                "writable": false,
                "default": "",
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 57354,
                "name": "ProductFamily",
                "type": "string",
                "length": 16,
                "writable": false,
                "default": "Wiser Home",
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 57355,
                "name": "VendorURL",
                "type": "string",
                "length": 64,
                "writable": false,
                "default": "http://www.schneider-electric.com",
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 65533,
                "name": "ClusterRevision",
                "type": "uint16",
                "writable": false,
                "default": 0,
                "manufacturer": false
              }
            ],
            "commands": {
              "C->S": [
                {
                  "id": 0,
                  "desciption": "Reset to Factory Defaults",
                  "manatory": false,
                  "manufacturer": false
                }
              ],
              "S->C": []
            }
          },
          {
            "id": 3,
            "name": "Identify",
            "manufacturer": false,
            "attributes": [
              {
                "id": 0,
                "name": "IdentifyTime",
                "type": "uint16",
                "writable": true,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 65533,
                "name": "ClusterRevision",
                "type": "uint16",
                "writable": true,
                "default": 1,
                "manufacturer": false
              }
            ],
            "commands": {
              "C->S": [
                {
                  "id": 0,
                  "description": "Identify",
                  "manufacturer": false
                },
                {
                  "id": 1,
                  "description": "Identify Query",
                  "manufacturer": false
                }
              ],
              "S->C": [
                {
                  "id": 0,
                  "description": "Identify Query Response",
                  "manufacturer": false
                }
              ]
            }
          },
          {
            "id": 4,
            "name": "Groups",
            "manufacturer": false,
            "attributes": [
              {
                "id": 0,
                "name": "NameSupport",
                "type": "map8",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 65533,
                "name": "ClusterRevision",
                "type": "uint16",
                "writable": false,
                "default": 0,
                "manufacturer": false
              }
            ],
            "commands": {
              "C->S": [
                {
                  "id": 0,
                  "description": "Add group",
                  "manufacturer": false
                },
                {
                  "id": 1,
                  "description": "View group",
                  "manufacturer": false
                },
                {
                  "id": 2,
                  "description": "Get group membership",
                  "manufacturer": false
                },
                {
                  "id": 3,
                  "description": "Remove group",
                  "manufacturer": false
                },
                {
                  "id": 4,
                  "description": "Remove all groups",
                  "manufacturer": false
                },
                {
                  "id": 5,
                  "description": "Add group if identifying",
                  "manufacturer": false
                }
              ],
              "S->C": [
                {
                  "id": 0,
                  "description": "Add group response",
                  "manufacturer": false
                },
                {
                  "id": 1,
                  "description": "View group response",
                  "manufacturer": false
                },
                {
                  "id": 2,
                  "description": "Get group membership response",
                  "manufacturer": false
                },
                {
                  "id": 3,
                  "description": "Remove group response",
                  "manufacturer": false
                }
              ]
            }
          },
          {
            "id": 5,
            "name": "Scenes",
            "manufacturer": false,
            "attributes": [
              {
                "id": 0,
                "name": "SceneCount",
                "type": "uint8",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 1,
                "name": "CurrentScene",
                "type": "uint8",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 2,
                "name": "CurrentGroup",
                "type": "uint16",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 3,
                "name": "SceneValid",
                "type": "bool",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 4,
                "name": "NameSupport",
                "type": "map8",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 65533,
                "name": "ClusterRevision",
                "type": "uint16",
                "writable": false,
                "default": 0,
                "manufacturer": false
              }
            ],
            "commands": {
              "C->S": [
                {
                  "id": 0,
                  "description": "Add Scene",
                  "manufacturer": false
                },
                {
                  "id": 1,
                  "description": "View Scene",
                  "manufacturer": false
                },
                {
                  "id": 2,
                  "description": "Remove Scene",
                  "manufacturer": false
                },
                {
                  "id": 3,
                  "description": "Remove All Scenes",
                  "manufacturer": false
                },
                {
                  "id": 4,
                  "description": "Store Scene",
                  "manufacturer": false
                },
                {
                  "id": 5,
                  "description": "Recall Scene",
                  "manufacturer": false
                },
                {
                  "id": 6,
                  "description": "Get Scene Membership",
                  "manufacturer": false
                }
              ],
              "S->C": []
            }
          },
          {
            "id": 6,
            "name": "On/Off",
            "manufacturer": false,
            "attributes": [
              {
                "id": 0,
                "name": "OnOff",
                "type": "bool",
                "writable": false,
                "default": 0,
                "manufacturer": false
              },
              {
                "id": 65533,
                "name": "ClusterRevision",
                "type": "uint16",
                "writable": false,
                "default": 1,
                "manufacturer": false
              }
            ],
            "commands": {
              "C->S": [
                {
                  "id": 0,
                  "description": "Off",
                  "manufacturer": false
                },
                {
                  "id": 1,
                  "description": "On",
                  "manufacturer": false
                },
                {
                  "id": 2,
                  "description": "Toggle",
                  "manufacturer": false
                }
              ],
              "S->C": []
            }
          },
          {
            "id": 64516,
            "name": "Visa Configuration",
            "manufacturer": true,
            "manufacturer_code": 4190,
            "attributes": [
              {
                "id": 0,
                "name": "IndicatorLuminanceLevel",
                "type": "uint8",
                "writable": true,
                "default": 0,
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 1,
                "name": "IndicatorColor",
                "type": "uint8",
                "writable": true,
                "default": 0,
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 2,
                "name": "Indicator Mode",
                "type": "uint8",
                "writable": true,
                "default": 0,
                "manufacturer": true,
                "manufacturer_code": 4190
              },
              {
                "id": 65533,
                "name": "ClusterRevision",
                "type": "uint16",
                "writable": true,
                "default": 1,
                "manufacturer": true,
                "manufacturer_code": 4190
              }
            ],
            "commands": {
              "C->S": [],
              "S->C": []
            }
          }
        ]
      }
    ],
    "node": {
      "device_type": "router",
      "manufacturer_code": 4190,
      "radio_power": 10
    }
  }
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|object| 否 |none|
|» filename|body|string| 是 |none|
|» config|body|object| 是 |none|
|»» endpoints|body|[object]| 是 |none|
|»»» client_clusters|body|[object]| 否 |none|
|»»»» attributes|body|[object]| 是 |none|
|»»»»» default|body|any| 是 |none|
|»»»»»» *anonymous*|body|string| 否 |none|
|»»»»»» *anonymous*|body|integer| 否 |none|
|»»»»» id|body|integer| 是 |none|
|»»»»» length|body|integer| 否 |none|
|»»»»» manufacturer|body|boolean| 是 |none|
|»»»»» manufacturer_code|body|integer| 否 |none|
|»»»»» name|body|string| 否 |none|
|»»»»» type|body|string| 是 |none|
|»»»»» writable|body|boolean| 是 |none|
|»»»» commands|body|object| 是 |none|
|»»»»» S->C|body|[object]| 是 |none|
|»»»»»» description|body|string| 否 |none|
|»»»»»» id|body|integer| 是 |none|
|»»»»»» manufacturer|body|boolean| 是 |none|
|»»»»»» manufacturer_code|body|integer| 否 |none|
|»»»»» C->S|body|[object]| 是 |none|
|»»»»»» description|body|string| 否 |none|
|»»»»»» id|body|integer| 是 |none|
|»»»»»» manufacturer|body|boolean| 是 |none|
|»»»»»» manufacturer_code|body|integer| 否 |none|
|»»»» id|body|integer| 是 |none|
|»»»» manufacturer|body|boolean| 是 |none|
|»»»» manufacturer_code|body|integer| 否 |none|
|»»»» name|body|string| 是 |none|
|»»» device_id|body|integer| 否 |none|
|»»» device_version|body|integer| 否 |none|
|»»» id|body|integer| 否 |none|
|»»» profile_id|body|integer| 否 |none|
|»»» server_clusters|body|[object]| 否 |none|
|»»»» attributes|body|[object]| 是 |none|
|»»»»» default|body|any| 是 |none|
|»»»»»» *anonymous*|body|string| 否 |none|
|»»»»»» *anonymous*|body|integer| 否 |none|
|»»»»» id|body|integer| 是 |none|
|»»»»» length|body|integer| 否 |none|
|»»»»» manufacturer|body|boolean| 是 |none|
|»»»»» manufacturer_code|body|integer| 否 |none|
|»»»»» name|body|string| 否 |none|
|»»»»» type|body|string| 是 |none|
|»»»»» writable|body|boolean| 是 |none|
|»»»» commands|body|object| 是 |none|
|»»»»» S->C|body|[object]| 是 |none|
|»»»»»» description|body|string| 否 |none|
|»»»»»» id|body|integer| 是 |none|
|»»»»»» manufacturer|body|boolean| 是 |none|
|»»»»»» manufacturer_code|body|integer| 否 |none|
|»»»»» C->S|body|[object]| 是 |none|
|»»»»»» description|body|string| 否 |none|
|»»»»»» id|body|integer| 是 |none|
|»»»»»» manufacturer|body|boolean| 是 |none|
|»»»»»» manufacturer_code|body|integer| 否 |none|
|»»»» id|body|integer| 是 |none|
|»»»» manufacturer|body|boolean| 是 |none|
|»»»» manufacturer_code|body|integer| 否 |none|
|»»»» name|body|string| 否 |none|
|»» node|body|object| 是 |none|
|»»» device_type|body|string| 是 |none|
|»»» manufacturer_code|body|integer| 是 |none|
|»»» radio_power|body|integer| 是 |none|

> 返回示例

> 成功

```json
{
  "code": 0,
  "data": {},
  "timestamp": 1654746342252,
  "uuid": "a2bcec2b-e7a6-11ec-a523-1826492a4080",
  "message": ""
}
```

> 500 Response

```json
{
  "code": 0,
  "data": {},
  "timestamp": 0,
  "uuid": "string",
  "message": "string"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|服务器内部错误|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

状态码 **500**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

## PUT 批量更新设备配置

PUT /configs/devices

> Body 请求参数

```json
{
  "devices": [
    "94DEB8FFFEF11F35",
    "94DEB8FFFEF12311"
  ],
  "filename": "1G_Switch.yml"
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|object| 否 |none|
|» filename|body|string| 否 |none|
|» config|body|object| 否 |none|
|»» endpoints|body|[object]| 是 |none|
|»»» client_clusters|body|[object]| 是 |none|
|»»»» attributes|body|[object]| 是 |none|
|»»»»» default|body|any| 是 |none|
|»»»»»» *anonymous*|body|string| 否 |none|
|»»»»»» *anonymous*|body|integer| 否 |none|
|»»»»» id|body|integer| 是 |none|
|»»»»» length|body|integer| 否 |none|
|»»»»» manufacturer|body|boolean| 是 |none|
|»»»»» manufacturer_code|body|integer| 否 |none|
|»»»»» name|body|string| 否 |none|
|»»»»» type|body|string| 是 |none|
|»»»»» writable|body|boolean| 是 |none|
|»»»» commands|body|object| 是 |none|
|»»»»» S->C|body|[object]| 是 |none|
|»»»»»» description|body|string| 否 |none|
|»»»»»» id|body|integer| 是 |none|
|»»»»»» manufacturer|body|boolean| 是 |none|
|»»»»»» manufacturer_code|body|integer| 否 |none|
|»»»»» C->S|body|[object]| 是 |none|
|»»»»»» description|body|string| 否 |none|
|»»»»»» id|body|integer| 是 |none|
|»»»»»» manufacturer|body|boolean| 是 |none|
|»»»»»» manufacturer_code|body|integer| 否 |none|
|»»»» id|body|integer| 是 |none|
|»»»» manufacturer|body|boolean| 是 |none|
|»»»» manufacturer_code|body|integer| 否 |none|
|»»»» name|body|string| 是 |none|
|»»» device_id|body|integer| 是 |none|
|»»» device_version|body|integer| 是 |none|
|»»» id|body|integer| 是 |none|
|»»» profile_id|body|integer| 是 |none|
|»»» server_clusters|body|[object]| 是 |none|
|»»»» attributes|body|[object]| 是 |none|
|»»»»» default|body|any| 是 |none|
|»»»»»» *anonymous*|body|string| 否 |none|
|»»»»»» *anonymous*|body|integer| 否 |none|
|»»»»» id|body|integer| 是 |none|
|»»»»» length|body|integer| 否 |none|
|»»»»» manufacturer|body|boolean| 是 |none|
|»»»»» manufacturer_code|body|integer| 否 |none|
|»»»»» name|body|string| 否 |none|
|»»»»» type|body|string| 是 |none|
|»»»»» writable|body|boolean| 是 |none|
|»»»» commands|body|object| 是 |none|
|»»»»» S->C|body|[object]| 是 |none|
|»»»»»» description|body|string| 否 |none|
|»»»»»» id|body|integer| 是 |none|
|»»»»»» manufacturer|body|boolean| 是 |none|
|»»»»»» manufacturer_code|body|integer| 否 |none|
|»»»»» C->S|body|[object]| 是 |none|
|»»»»»» description|body|string| 否 |none|
|»»»»»» id|body|integer| 是 |none|
|»»»»»» manufacturer|body|boolean| 是 |none|
|»»»»»» manufacturer_code|body|integer| 否 |none|
|»»»» id|body|integer| 是 |none|
|»»»» manufacturer|body|boolean| 是 |none|
|»»»» manufacturer_code|body|integer| 否 |none|
|»»»» name|body|string| 是 |none|
|»» node|body|object| 是 |none|
|»»» device_type|body|string| 是 |none|
|»»» manufacturer_code|body|integer| 是 |none|
|»»» radio_power|body|integer| 是 |none|
|» devices|body|[string]| 是 |none|

> 返回示例

> 成功

```json
{
  "code": 0,
  "message": "",
  "timestamp": 1654757403472,
  "uuid": "63bd27b1-e7c0-11ec-878e-1826492a4080",
  "data": {}
}
```

> 服务器内部错误

```json
{
  "code": 10000,
  "data": {},
  "timestamp": 1654757427096,
  "uuid": "71d1dfca-e7c0-11ec-b194-1826492a4080",
  "message": "device 94DEB8FFFEF1231 not exist"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|服务器内部错误|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» message|string|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» data|object|true|none||none|

状态码 **500**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|true|none||none|
|» data|object|true|none||none|
|» timestamp|integer|true|none||none|
|» uuid|string|true|none||none|
|» message|string|true|none||none|

# api/2/auto

## GET 获取内置自动测试功能列表

GET /auto

> 返回示例

> 200 Response

```json
{}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### 返回数据结构

## POST 触发指定的内置自动化测试

POST /auto/scripts/{script}

> Body 请求参数

```json
{}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|script|path|string| 是 |内置自动化测试脚本名称，包含capacity（容量测试），stability（稳定性测试）等|
|body|body|object| 否 |none|

> 返回示例

> 200 Response

```json
{}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### 返回数据结构

## GET 获取指定的内置自动化测试配置

GET /auto/scripts/{script}/config

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|script|path|string| 是 |none|

> 返回示例

> 200 Response

```json
{}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### 返回数据结构

## PUT 修改指定的内置自动化测试配置

PUT /autos/{script}/config

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|script|path|string| 是 |none|

> 返回示例

> 200 Response

```json
{}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### 返回数据结构

## GET 获取自动化脚本信息

GET /auto/{operation}

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|operation|path|string| 是 |running, history, records|

> 返回示例

> 200 Response

```json
{}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### 返回数据结构

# 数据模型

