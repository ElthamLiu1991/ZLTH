FROM python:3

WORKDIR /usr/local/app
ADD requirements.txt ./
RUN pip install -r requirements.txt
ADD launcher.py .
ADD logConfig.json .
ADD version/ ./version
ADD templates/ ./templates
ADD zigbeeLauncher/ ./zigbeeLauncher

CMD [ "python", "launcher.py" ]
