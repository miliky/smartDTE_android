FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev make patch file unzip ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /work
ENV PYTHONDONTWRITEBYTECODE=1
