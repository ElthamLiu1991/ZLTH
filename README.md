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
`docker buildx build --platform linux/arm64/v8,linux/arm/v7 -t eltham/zigbee_launcher_testharness --push .`
## How to Run
Before running ZLTH service, please make sure a MQTT broker service already running on your machine
### Windows
#### python
`python launcher.py`
#### EXE
double click ***launcher.exe***
### Linux
`python launcher.py`
### Docker
## How to Use
Open web browser and enter: http://localhost:5000, or any ZLTH service IP address instead of *localhost*, **http://{ip}:5000**, enjoy!