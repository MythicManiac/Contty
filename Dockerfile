FROM python:3.7.2-alpine3.7

WORKDIR /code

COPY ./Contty/requirements.txt /code/requirements.txt

RUN pip install -U pip --no-cache && \
    pip install -r requirements.txt --no-cache

COPY ./Contty /code
RUN SECRET_KEY=xxx python manage.py collectstatic --noinput && \
    mkdir /contty/

ENTRYPOINT ["/code/entrypoint.sh"]
