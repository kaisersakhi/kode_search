FROM python:3.12.0

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir --upgrade pip  && pip install -r requirements.txt

COPY . /app

CMD sh -c 'python3 feeder.py'
