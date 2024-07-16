FROM ubuntu
LABEL name yamuna
RUN apt update -y
RUN apt install apache2 -y
COPY . /usr/www/html
CMD ["/usr/sbin/apachectl", "-D", "FOREGROUND"]
