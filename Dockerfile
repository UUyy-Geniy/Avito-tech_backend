FROM python:3.9
ENV PYTHONUNBUFFERED 1
WORKDIR /banner_service
EXPOSE 8000
COPY requirements.txt requirements.txt
RUN apt-get update \
    && python -m pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN adduser --disabled-password service-user