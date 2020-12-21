FROM python:3.8-slim

RUN pip install pipenv; mkdir -p /app/data
COPY . /app
WORKDIR /app
RUN pipenv install
