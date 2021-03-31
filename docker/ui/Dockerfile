FROM python:3.8-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /usr/src/app

RUN pip install --upgrade pip
RUN pip install -r requirements/common.txt

CMD gunicorn --timeout ${LAW_FETCHER_GUNICORN_TIMEOUT} -w ${LAW_FETCHER_GUNICORN_UI_WORKERS} --bind 0.0.0.0:${LAW_FETCHER_UI_PORT} --reload --log-level=debug law_fetcher.entrypoints.ui.run:app