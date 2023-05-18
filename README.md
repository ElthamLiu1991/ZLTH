# ZIGBEE Launcher Test Harness
ZIGBEE Launcher Test Harness is a local web service
## Communication Structure
## File Structure
- launcher.py: main entry
- config.json
- requirements.txt
- version.py
- version_file.txt
- zigbeeLauncher\
- templates\
- scripts\
- version\
- windows_component\
- documents\

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
`pyinstaller.exe -F -p .\venv\Lib\site-packages\ -w -i .\windows_component\logo.ico --version-file .\version_file.txt launcher.py --hidden-import engineio.async_drivers.threading`
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