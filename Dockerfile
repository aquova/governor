# Run with 'docker run -v $(pwd):/governor -it governor sh'
FROM aquova/commonbot:1.0.0

RUN apk update && apk add \
    freetype-dev \
    jpeg-dev \
    zlib-dev

ADD requirements.txt /governor/requirements.txt
RUN pip3 install -r /governor/requirements.txt
