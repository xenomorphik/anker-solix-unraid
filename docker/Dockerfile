FROM python:3.12-alpine

RUN apk add --no-cache git tzdata
RUN pip install --no-cache-dir \
    aiohttp \
    aiofiles \
    cryptography \
    paho-mqtt \
    git+https://github.com/thomluther/anker-solix-api.git

WORKDIR /app
COPY solix_mqtt_poller.py /app/solix_mqtt_poller.py
RUN chmod +x /app/solix_mqtt_poller.py

CMD ["python3", "-u", "/app/solix_mqtt_poller.py"]
