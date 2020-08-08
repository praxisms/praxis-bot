FROM python:3.8-slim-buster

ARG   apsw_version="3.32.2-r1"
ARG sqlite_version="3.32.2"

RUN apt-get update && apt-get install -y \
  build-essential \
  git \
  wget

WORKDIR /praxis-bot
COPY . .
RUN pip install \
    https://github.com/rogerbinns/apsw/releases/download/${apsw_version}/apsw-${apsw_version}.zip \
    --global-option=fetch --global-option=--version --global-option=${sqlite_version} --global-option=--all \
    --global-option=build --global-option=--enable-all-extensions
RUN python setup.py install
ENTRYPOINT ["praxisbot"]
