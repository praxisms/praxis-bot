FROM praxisms/praxis-bot-base:2020-08-09

WORKDIR /praxis-bot
COPY . .
RUN pip install -r docker-requirements.txt
RUN python setup.py install
ENTRYPOINT ["praxisbot"]
