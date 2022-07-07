FROM python:3.8-slim-buster
ADD . /python-flask
WORKDIR /python-flask
EXPOSE 5000
RUN python -m pip install -r requirements.txt
CMD ["python","./app.py"]