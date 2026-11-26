FROM caddy:2 AS caddy
FROM python:3.12-slim
COPY --from=caddy /usr/bin/caddy /usr/bin/caddy
WORKDIR /app
COPY apify_connection_check.py /app/apify_connection_check.py
COPY index.html /srv/index.html
COPY os-one /srv/os-one
RUN printf ':8080 {\n root * /srv\n file_server\n}\n' > /app/Caddyfile
EXPOSE 8080
CMD ["sh", "-c", "python /app/apify_connection_check.py; exec caddy run --config /app/Caddyfile --adapter caddyfile"]
