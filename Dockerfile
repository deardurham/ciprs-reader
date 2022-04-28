FROM python:3.8-slim

WORKDIR /tmp

RUN set -ex \
    && BUILD_DEPS=" \
    curl \
    build-essential \
    zlib1g-dev \
    libpng-dev \
    libjpeg-dev \
    pkg-config \
    libfontconfig1-dev \
    " \
    && apt-get update \
    && apt-get install -y --no-install-recommends $BUILD_DEPS

# Install poppler pdftotext, based on xpdf3 (the old version)
RUN set -ex \
    && curl -k https://poppler.freedesktop.org/poppler-0.57.0.tar.xz | tar xJ \
    && chmod -R 755 ./poppler-0.57.0 \
    && cd ./poppler-0.57.0/ \
	&&./configure \
	  --prefix=/tmp/poppler \
	  --disable-shared \
	  --enable-build-type=release \
	  --enable-libopenjpeg=none \
    && make install \
    && cp /tmp/poppler/bin/pdftotext /usr/local/bin/pdftotext

RUN set -ex \
    && RUN_DEPS=" \
    libfontconfig \
    wget \
    git \
    " \
    && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
    && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
    && rm -rf /var/lib/apt/lists/*

RUN set -ex \
    && wget --no-check-certificate https://dl.xpdfreader.com/xpdf-tools-linux-4.04.tar.gz \
    && tar -xvf xpdf-tools-linux-4.04.tar.gz \
    && cp xpdf-tools-linux-4.04/bin64/pdftotext /usr/local/bin/pdftotext-4

COPY ./requirements.txt /requirements.txt

RUN set -ex \
    && pip install --no-cache-dir -r /requirements.txt

WORKDIR /usr/src/app
