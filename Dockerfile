FROM python:3

RUN curl https://xpdfreader-dl.s3.amazonaws.com/old/xpdf-3.04.tar.gz | tar xz
RUN chmod -R 755 ./xpdf-3.04 && cd ./xpdf-3.04/ && ./configure && make && make install

WORKDIR /usr/src/app
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt