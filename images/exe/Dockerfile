FROM ubuntu:16.04

ENV SSL_CERT_DIR=/etc/ssl/certs

RUN apt-get update && apt-get -yq install python-setuptools python-zope.interface python-imaging python-chardet python-lxml python-feedparser mimetex python-git

RUN apt-get update && apt-get -yq install python-pip python-dev libxml2-dev libxmlsec1-dev swig

RUN apt-get update && apt-get -yq install python-m2crypto python-isodate python-defusedxml

RUN apt-get update && apt-get -yq install python-bs4 python-oauth2client python-googleapi

RUN apt-get update && apt-get -yq install python-passlib 

RUN apt-get update && apt-get -yq install fuseext2

RUN apt-get update && apt-get -yq install python-suds python-requests-oauthlib python-dateutil

RUN pip install dm.xmlsec.binding==1.3.2

RUN apt-get update && apt-get -yq install cssmin python-webassets

RUN apt-get update && apt-get -yq install python-certifi python-pil

RUN pip install pyjwt

COPY . /home/app

COPY images/exe/example.crt /usr/local/share/ca-certificates/intef-es-chain.crt

RUN update-ca-certificates

ADD images/exe/run.sh /run.sh

RUN mkdir /var/run/exe

WORKDIR /home/app

CMD /run.sh
