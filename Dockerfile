FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates xz-utils && \
    curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar -xJ && \
    mv ffmpeg-*-static/ffmpeg /usr/local/bin/ && \
    rm -rf ffmpeg-*-static && \
    apt-get purge -y curl xz-utils && \
    rm -rf /var/lib/apt/lists/*

ADD . /app

RUN uv sync --locked --no-dev

CMD ["uv", "run", "--no-default-groups", "main.py"]