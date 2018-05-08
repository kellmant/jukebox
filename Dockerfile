############################################################
# Dockerfile to build Apollo Cloud
############################################################
# Set the base image
FROM debian:latest
# Original author is Carlos Tighe
MAINTAINER Kellman
# Install packages
RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi build-essential \
    python python-dev python-pip \
    vim curl libav-tools && \
    groupadd -g 800 media && \
    apt-get clean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/*
# Copy over and install the requirements
COPY ./app/requirements.txt /var/www/apollo-cloud/app/requirements.txt
RUN pip install -r /var/www/apollo-cloud/app/requirements.txt
RUN pip install -U youtube-dl
# Copy over the apache configuration file and enable the site
COPY ./apollo-cloud.conf /etc/apache2/sites-available/apollo-cloud.conf
RUN a2ensite apollo-cloud
RUN a2enmod headers
# Copy over the wsgi file
COPY ./apollo-cloud.wsgi /var/www/apollo-cloud/apollo-cloud.wsgi
COPY ./run.py /var/www/apollo-cloud/run.py
COPY ./app /var/www/apollo-cloud/app/
COPY ./docker-entrypoint.sh /
RUN a2dissite 000-default.conf
RUN a2ensite apollo-cloud.conf
# Set permissions for the static directory
RUN chmod -R 777 /var/www/apollo-cloud/app/static/  
RUN usermod -u 804 www-data && usermod -g 800 www-data
VOLUME ["/var/www/apollo-cloud/app/static/songs"]
EXPOSE 80
WORKDIR /var/www/apollo-cloud
ENTRYPOINT ["/docker-entrypoint.sh"]
