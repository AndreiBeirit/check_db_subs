FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update \
    && apt-get -y install cron nano tzdata \
    && ln -fs /usr/share/zoneinfo/Asia/Yekaterinburg /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && touch /var/log/cron.log \
    && chmod 777 /var/log/cron.log

COPY . .

COPY cronjob /etc/cron.d/cronjob

RUN chmod 0644 /etc/cron.d/cronjob \
    && crontab /etc/cron.d/cronjob

ENV user=${user_db}
ENV password=${password_db}
ENV host=${host_db}
ENV database=${database_db}
ENV SLACK_WEBHOOK=${SLACK_WEBHOOK}

CMD cron && tail -f /var/log/cron.log
