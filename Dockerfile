FROM python:3.6-alpine
WORKDIR /app
ADD . /app/
RUN apk --update add --no-cache mariadb-dev build-base gcc musl-dev libffi-dev libjpeg zlib tiff-dev \
    && pip install --no-cache-dir --trusted-host pypi.python.org -r /app/requirements.txt \
    && addgroup -g 1000 -S app \
    && adduser -u 1000 -S app -G app \
    && chmod +r -R /app \
    && chown app:app -R /app
USER app
CMD ["/usr/local/bin/gunicorn", "room_reservation.wsgi:application", \
    "--pid", "/app/logs/app.pid", \
    "--user", "app", \
    "--timeout", "60", \
    "--bind", "0.0.0.0:9010", \
    "--log-level", "warning"]

