FROM python:3.11-alpine

RUN apk update && apk add \
    build-base \
    freetype-dev \
    jpeg-dev \
    zlib-dev

ADD requirements.txt /governor/requirements.txt
RUN pip3 install -r /governor/requirements.txt

WORKDIR /governor
CMD ["python3", "-u", "main.py"]
