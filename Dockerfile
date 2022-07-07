FROM python:3.8-slim-buster
ADD . /python-flask
WORKDIR /python-flask
RUN python -m pip install -r requirements.txt
EXPOSE 8000
CMD ["flask","run"]