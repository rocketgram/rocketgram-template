FROM python:3.7-alpine

COPY requirements.txt /opt/

RUN apk update && \
    apk add --no-cache ca-certificates && \
    pip install -r /opt/requirements.txt --no-use-pep517 --no-cache-dir -q --compile && \
    rm -rf /var/cache/apk/* &&

COPY app/ /opt/app/

WORKDIR /opt/app

CMD ["python", "/app/engine.py"]
