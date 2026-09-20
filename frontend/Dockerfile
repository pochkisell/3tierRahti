# syntax=docker/dockerfile:1
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html /usr/share/nginx/html/index.html
COPY documentation.html /usr/share/nginx/html/documentation.html
COPY images/ /usr/share/nginx/html/images/

EXPOSE 8080
