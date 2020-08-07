FROM python:3.8-alpine3.12

RUN apk add --no-cache \
  git \
  wget

WORKDIR /praxis-bot
COPY . .
RUN python setup.py install
ENTRYPOINT ["praxisbot"]
