FROM python:3

WORKDIR /usr/local/app
ADD requirements.txt ./
RUN pip install -r requirements.txt
ADD run_flask.py .
ADD version/ ./version
ADD zigbeeLauncher/ ./zigbeeLauncher

CMD [ "python", "run_flask.py" ]
