FROM python:3.8-slim AS base
RUN apt-get update && apt-get install --no-install-recommends --yes python3

RUN pip install praw
RUN pip install pika
RUN pip install python-dotenv

ENV PYTHONUNBUFFERED 1

COPY . reddit_img/

CMD ["python", "reddit_img/prawComponent.py"]