FROM python:3.11-slim

WORKDIR /app
COPY . /app

# install system deps & Python libs
RUN apt-get update && apt-get install -y --no-install-recommends gcc default-libmysqlclient-dev pkg-config \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# copy entrypoint
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

ENV FLASK_APP=src
ENTRYPOINT ["./start.sh"]

