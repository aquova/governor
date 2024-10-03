FROM ghcr.io/astral-sh/uv:python3.12-alpine

RUN apk update && apk add \
    build-base \
    freetype-dev \
    jpeg-dev \
    zlib-dev

ADD . /governor
WORKDIR /governor
RUN uv sync --frozen
CMD ["uv", "run", "src/main.py"]
