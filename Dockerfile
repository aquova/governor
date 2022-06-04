FROM aquova/commonbot:2.0.0b3

RUN apk update && apk add \
    freetype-dev \
    jpeg-dev \
    zlib-dev

ADD requirements.txt /governor/requirements.txt
RUN pip3 install -r /governor/requirements.txt

CMD ["python3", "-u", "/governor/main.py"]
