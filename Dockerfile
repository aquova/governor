FROM aquova/discord.py:1.5.1

RUN apk update && apk add \
    freetype-dev \
    jpeg-dev \
    zlib-dev

ADD requirements.txt /governor/requirements.txt
RUN pip3 install -r /governor/requirements.txt
