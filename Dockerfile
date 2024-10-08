FROM python:3.9-alpine3.13
LABEL maintainer="ricosappdev.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./app /app

WORKDIR  /app
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev && \ 
    /py/bin/pip install -r /requirements.txt && \
    apk del .tmp-deps && \ 
    adduser --disabled-password --no-create-home app && \
    chown -R app:app /app && \ 
    chmod -R 755 /app 


ENV PATH="/py/bin:$PATH"

USER app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi:application"]



