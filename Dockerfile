FROM python:3

WORKDIR /usr/local/app
ADD requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.douban.com/simple
ADD launcher.py .
ADD config.json .
ADD version/ ./version
ADD templates/ ./templates
ADD scripts/ ./scripts
ADD dcf/ ./dcf
ADD zigbeeLauncher/ ./zigbeeLauncher

CMD [ "python", "launcher.py" ]
