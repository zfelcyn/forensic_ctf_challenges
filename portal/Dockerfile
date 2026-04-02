FROM python:3.12-alpine AS builder

WORKDIR /app

COPY challenges ./challenges
COPY public ./public
COPY scripts ./scripts

RUN python3 scripts/build_registry.py

FROM nginx:1.27-alpine

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/public /usr/share/nginx/html

EXPOSE 8080
