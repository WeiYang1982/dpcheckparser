FROM python:3.9.10-buster
MAINTAINER wei.yang
ADD . /app

ENV TZ "Asia/Shanghai"

WORKDIR /app

RUN  chmod a+x /app/*
RUN  pip install -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD python3 ./dpcheck_parser.py
