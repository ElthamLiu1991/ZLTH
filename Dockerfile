FROM python:3

WORKDIR /usr/local/app
ADD requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.douban.com/simple
ADD launcher.py .
ADD logConfig.json .
ADD version/ ./version
ADD templates/ ./templates
Add scripts/ ./scripts
ADD zigbeeLauncher/ ./zigbeeLauncher

CMD [ "python", "launcher.py" ]
