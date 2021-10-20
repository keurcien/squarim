FROM python:3.8-slim-buster

COPY requirements.txt ./

RUN apt-get update \
    && apt-get -y install libglib2.0-0 \
    && pip install -r requirements.txt \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY app ./app

ENTRYPOINT ["python", "app/app.py"]

