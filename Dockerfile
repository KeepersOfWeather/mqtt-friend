FROM python:latest

WORKDIR /root

# These should be set, the program will not work otherwise
ENV BROKER_ADDRESS=
ENV BROKER_PORT=
ENV BROKER_USER=
ENV BROKER_PASSWORD=
ENV DB_USER=
ENV DB_PASSWORD=
ENV DB_ENDPOINT=
ENV DB_PORT=
ENV DB_DB=
ENV DB_JSON_TABLE=

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./mqtt.py" ]