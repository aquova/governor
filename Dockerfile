# Run with 'docker run -d -v $(pwd):/governor governor'
FROM aquova/commonbot:1.2.0

RUN apk update && apk add \
    freetype-dev \
    jpeg-dev \
    zlib-dev

ADD requirements.txt /governor/requirements.txt
RUN pip3 install -r /governor/requirements.txt

CMD ["python3", "-u", "/governor/src/main.py"]
