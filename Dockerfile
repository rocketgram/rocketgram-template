FROM python:3.10

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt --no-cache-dir -q --compile

COPY app/ /opt/app/

WORKDIR /opt/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONOPTIMIZE=2

CMD ["python", "/opt/app/engine.py"]
