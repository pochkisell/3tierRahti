FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html /usr/share/nginx/html/index.html
COPY documentation.html /usr/share/nginx/html/documentation.html
COPY week5.html /usr/share/nginx/html/week5.html
COPY week6.html /usr/share/nginx/html/week6.html
COPY images/ /usr/share/nginx/html/images/

EXPOSE 8080
