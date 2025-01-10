FROM python:3.12.8-alpine3.20 AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add --no-cache --virtual .build-deps gcc musl-dev

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.12.8-alpine3.20

ENV PROJECT_DIR=/app
WORKDIR $PROJECT_DIR

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY ./app_entrypoint.dev.sh .
RUN sed -i 's/\r$//g' $PROJECT_DIR/app_entrypoint.dev.sh
RUN chmod +x $PROJECT_DIR/app_entrypoint.dev.sh

COPY . .

CMD ["sh", "/app/app_entrypoint.dev.sh"]