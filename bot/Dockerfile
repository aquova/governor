FROM ghcr.io/astral-sh/uv:python3.12-alpine

COPY . /governor
WORKDIR /governor
RUN uv sync --frozen
CMD ["uv", "run", "main.py"]
