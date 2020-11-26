[![Build Status](https://travis-ci.org/reuseman/GoOutSafe.svg?branch=main)](https://travis-ci.org/reuseman/GoOutSafe) [![Coverage Status](https://coveralls.io/repos/github/reuseman/GoOutSafe/badge.svg?branch=main)](https://coveralls.io/github/reuseman/GoOutSafe?branch=main) 

# What is this?
This is an attempt to realize an online restaurant reservation platform with user tracking capabilities for Covid-19 purposes.

It was created by a team of 5 people in 2020, for the exam of Advanced Software Engineering at University of Pisa. 

The idea was to create the system as a [Monolith][1] architecture and then split it in **Microservices**, in order to get an overview and understand all the facets and difficulties of the whole process.

## User stories
![](docs/user-stories.png)

## Architecture
![](docs/architecture.png)

# Getting started

## Docker-compose
Create a `.env.docker` file with the following environment variables:
    SECRET_KEY=your_secret_key1
    WTF_CSRF_SECRET_KEY=your_secret_key2

    MAIL_USERNAME=yourserver@mail.com
    MAIL_PASSWORD=yourpassword
    MAIL_SERVER=smtp.server.com 

    REDIS_URL=redis://redis:6379/1

    CELERY_BROKER_URL=redis://redis:6379/0
    CELERY_RESULT_BACKEND=redis://redis:6379/0

    MYSQL_ROOT_PASSWORD=example
    MYSQL_USER=gooutsafe
    MYSQL_PASSWORD=my-secret-pw
    MYSQL_DATABASE=gooutsafe
    DATABASE_URI=mysql+pymysql://gooutsafe:my-secret-pw@database/gooutsafe

    URL_API_USER = "http://api-gateway:5000/"
    URL_API_BOOKING = "http://api-gateway:5000/"
    URL_API_RESTAURANT = "http://api-gateway:5000/"
    URL_API_CELERY = "http://api-gateway:5000/"
    ELASTICSEARCH_URL = "http://elastic-search:9200/"

To run

    docker-compose up


[1]: https://github.com/Squad002/GoOutSafe-Monolith