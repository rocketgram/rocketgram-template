FROM python:3.9-alpine

COPY requirements.txt /opt/

RUN apk update && \
    apk add --no-cache ca-certificates && \
    apk add --no-cache --virtual .build-deps gcc musl-dev

RUN pip install -r /opt/requirements.txt --no-use-pep517 --no-cache-dir -q --compile

RUN apk del .build-deps gcc musl-dev && \
    rm -rf /var/cache/apk/*

COPY app/ /opt/app/

WORKDIR /opt/app

CMD ["python", "/opt/app/engine.py"]
