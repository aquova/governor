FROM ghcr.io/astral-sh/uv:python3.12-alpine

RUN apk update && apk add \
    build-base \
    freetype-dev \
    jpeg-dev \
    zlib-dev

COPY . /governor
WORKDIR /governor
RUN uv sync --frozen
CMD ["uv", "run", "main.py"]
