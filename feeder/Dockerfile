FROM python:3.12.0

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir --upgrade pip  && pip install -r requirements.txt

ARG SHARED_DATA_PATH

ENV SHARED_DATA_PATH=$SHARED_DATA_PATH

CMD sh -c 'python3 /app/feeder.py $SHARED_DATA_PATH'