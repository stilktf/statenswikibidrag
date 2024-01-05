FROM python:3.12-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8080

ENTRYPOINT ["/bin/sh", "-c", "waitress-serve --port=8080 'app:app'"]