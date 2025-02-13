FROM python:3.12.0

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir --upgrade pip  && pip install -r requirements.txt

CMD sh -c 'python3 feeder.py'
