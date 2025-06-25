FROM python:3.11-bullseye

WORKDIR /app

COPY ./ /app

RUN python -m pip install -r requirements.txt

RUN python -m pip install gunicorn

CMD ["sh", "-c", "gunicorn --config gunicorn.conf.py main:app"]
