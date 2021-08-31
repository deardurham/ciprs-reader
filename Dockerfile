FROM debian:buster-slim AS xpdf3

RUN set -ex \
    && BUILD_DEPS=" \
    curl \
    build-essential \
    zlib1g-dev \
    libpng-dev \
    " \
    && apt-get update \
    && apt-get install -y --no-install-recommends $BUILD_DEPS

# Install pdftotext 3.04 (the old version)
RUN set -ex \
    && curl -k https://dl.xpdfreader.com/old/xpdf-3.04.tar.gz | tar xz \
    && chmod -R 755 ./xpdf-3.04 \
    && cd ./xpdf-3.04/ \
    && ./configure \
    && make \
    && make install

FROM python:3.8-slim

RUN set -ex \
    && RUN_DEPS=" \
    libfontconfig \
    wget \
    git \
    " \
    && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
    && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
    && rm -rf /var/lib/apt/lists/*

# Install pdftotext 4.03 (the new version)
RUN set -ex \
    && wget --no-check-certificate https://dl.xpdfreader.com/xpdf-tools-linux-4.03.tar.gz \
    && tar -xvf xpdf-tools-linux-4.03.tar.gz \
    && cp xpdf-tools-linux-4.03/bin64/pdftotext /usr/local/bin \
    && rm -rf xpdf-tools-linux-4.03*

COPY --from=xpdf3 /usr/local/bin/pdftotext /usr/local/bin/pdftotext-3.04

COPY ./requirements.txt /requirements.txt

RUN set -ex \
    && pip install --no-cache-dir -r /requirements.txt

WORKDIR /usr/src/app
