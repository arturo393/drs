FROM alpine/git
WORKDIR /
RUN apk --no-cache add curl \
    && curl -o Legacy.less https://raw.githubusercontent.com/Icinga/icingaweb2/support/2.9/public/css/icinga/legacy-theme.less \
    && curl -o select-icon-legacy.svg https://raw.githubusercontent.com/Icinga/icingaweb2/support/2.9/public/img/select-icon-legacy.svg \
    && git clone https://github.com/Icinga/icingadb-web.git icingadb

FROM icinga/icingaweb2:master
USER root
# RUN ln -s /usr/local/bin/icingacli /usr/bin/icingacli
RUN apt -y update && apt -y upgrade
# \    && apt install -y composer
RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" 
RUN php -r "if (hash_file('sha384', 'composer-setup.php') === '906a84df04cea2aa72f40b5f787e49f22d4c2f19492ac310e8cba5b96ac8b64115ac402c8cd292b8a03482574915d1a8') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;"  
RUN php composer-setup.php --install-dir=/usr/local/bin --filename=composer
RUN php -r "unlink('composer-setup.php');"
RUN composer self-update
ADD composer.json /usr/share/icinga-php/ipl/composer.json
RUN rm /usr/share/icinga-php/ipl/composer.lock
RUN composer require -d /usr/share/icinga-php/ipl ipl/stdlib:dev-master \
    && composer require -d /usr/share/icinga-php/ipl ipl/html:dev-master \
    && composer require -d /usr/share/icinga-php/ipl ipl/orm:dev-master \
    && composer require -d /usr/share/icinga-php/ipl ipl/sql:dev-master \
    && composer require -d /usr/share/icinga-php/ipl ipl/validator:dev-master \
    && composer require -d /usr/share/icinga-php/ipl ipl/web:dev-master \
    && composer update -d /usr/share/icinga-php/ipl
RUN rm -rf /usr/share/icingaweb2/modules/icingadb/*

ADD icingaweb2-module-elasticsearch /usr/share/icingaweb2/modules/elasticsearch

USER www-data
COPY --from=0 /icingadb /usr/share/icingaweb2/modules/icingadb
COPY --from=0 /Legacy.less /usr/share/icingaweb2/public/css/themes/Legacy.less
COPY --from=0 /select-icon-legacy.svg /usr/share/icingaweb2/public/img/select-icon-legacy.svg

RUN mkdir -p /data/etc/icingaweb2 && chmod -R 777 /data
