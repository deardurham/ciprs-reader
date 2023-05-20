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
    cmake \
    libfreetype6 \
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

# install xpdfreader pdftotext, which supports multiline description parsing
RUN set -ex \
    && curl -k https://dl.xpdfreader.com/xpdf-4.04.tar.gz | tar zxf - \
    && chmod -R 755 ./xpdf-4.04 \
    && cd ./xpdf-4.04/ \
    && mkdir build \
	&& cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_DISABLE_FIND_PACKAGE_Qt4=1 -DCMAKE_DISABLE_FIND_PACKAGE_Qt5Widgets=1 \
    && make \
    && cp xpdf/pdftotext /usr/local/bin/pdftotext-4

RUN set -ex \
    && RUN_DEPS=" \
    libfontconfig \
    wget \
    git \
    " \
    && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
    && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /requirements.txt

RUN set -ex \
    && pip install --no-cache-dir -r /requirements.txt

WORKDIR /usr/src/app
