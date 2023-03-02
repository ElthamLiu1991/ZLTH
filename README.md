# ZIGBEE Launcher Test Harness
ZIGBEE Launcher Test Harness is a local web service
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
`pyinstaller -F -p {project path}\myvenv\Lib\site-packages -w -i logo.ico --version-file version_file.txt launcher.py`
### Linux
1. setup python virtual environment: `python -m venv myvenv`
2. activate virtual environment: `source myvenv/bin/activate`
3. install modules: `pip install -r requirements.txt`, or use different package source: `pip install -r requirements.txt -i https://pypi.douban.com/simple`
### Docker
build docker image for different platform(Linux only)
`docker buildx build --platform linux/arm64/v8,linux/arm/v7 -t elthamliudocker/wiser_zigbee_launcher --push .`
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
Open web browser and enter: http://localhost:5000, enjoy!