# ZIGBEE Launcher Test Harness
ZIGBEE Launcher Test Harness is a local web service
## Communication Structure
![](/documents/ZLTH%20Communication%20Structure.png)
## File Structure
- **launcher.py**: application entry
- **config.json**: port and log configuration file
- **requirements.txt**: python libraries
- **version.py**: version control
- **version_file.txt**: windows application version configuration
- **zigbeeLauncher**
  - **api_2**: RESTFUL API definition
  - **auto_scripts**: automation testing
  - **database**: database definition
  - **dongle**: dongle operation
  - **logging**: logging configuration
  - **serial_protocol**: ZLTH serial protocol definition
  - **simulator**: MQTT client and client
  - **zigbee**: zigbee data type table
- **templates**: Web UI templates
- **scripts**: automation testing script configuration
- **version**: version file
- **windows_component**: dongle driver, EMQX MQTT broker

## Prepare
**python**: 3.9 or later\
**ZLTH dongle**: work with ZLTH service and run zigbee stack\
**EMQX MQTT Broker**: message communication, [EMQX Broker](https://www.emqx.io/downloads)
## How to Build
### Windows
1. setup python virtual environment: `python -m venv myvenv`
2. activate virtual environment: `myvenv\Scripts\activate`
3. install modules: `pip install -r requirements.txt`, or use different package source: `pip install -r requirements.txt -i https://pypi.douban.com/simple`
4. build executable application for windows:
`pyinstaller.exe -F -p .\venv\Lib\site-packages\ -w -i .\windows_component\logo.ico --version-file .\version_file.txt launcher.py --hidden-import engineio.async_drivers.threading --hidden-import zigbeeLauncher.auto_scripts.capacity --hidden-import zigbeeLauncher.auto_scripts.compose --hidden-import zigbeeLauncher.auto_scripts.stability
`
### Linux
1. setup python virtual environment: `python -m venv myvenv`
2. activate virtual environment: `source myvenv/bin/activate`
3. install modules: `pip install -r requirements.txt`, or use different package source: `pip install -r requirements.txt -i https://pypi.douban.com/simple`
### Docker
build docker image for different platform(Linux only)
`docker buildx build --platform linux/arm64/v8 -t registry.cn-hangzhou.aliyuncs.com/zlth/zigbee_launcher_testharness:[version] --push .`
## How to Run
Before running ZLTH service, please make sure a MQTT broker service already running on your machine
### Windows
#### python
`python launcher.py`
#### EXE
double click ***launcher.exe*** or ***run.bat***
### Linux
`python launcher.py`
### Docker
docker-compose.yml:
```yaml
version: '3'
services:
    zigbee_launcher:
        image: registry.cn-hangzhou.aliyuncs.com/zlth/zigbee_launcher_testharness
        network_mode: host
        volumes:
            - ./files:/usr/local/app/files
            - ./firmwares:/usr/local/app/firmwares
            - ./logs:/usr/local/app/logs
            - /dev:/dev
        privileged:
            true
```
run `docker-compose up` to start ZLTH service
## How to Use
Open web browser and enter: http://localhost:{port}(defined in *config.json*), or any ZLTH service IP address instead of *localhost*, **http://{ip}:{port}**
### Clients
ZLTH simulators information table.
### Device
ZLTH dongles information table.
### Update
Upgrade ZLTH dongle firmware.
### Operator
Interface to operate on or more ZLTH dongles, current support "join", "leave", "write" feature.
### Configure
Update dongle application, simulating to any existing or new zigbee product.
### Automation Testing
Opening automation testing script by /api/2/auto/scripts/{script name}, currently support "capacity", "stability" and "compose".
#### capacity
#### stability
#### compose
