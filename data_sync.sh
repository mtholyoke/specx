#!/bin/bash

# This should be run as root from /etc/crontab (or similar) to make
# a daily copy of the current Mossbauer data. Yesterday’s copy is
# saved just in case something goes weird.

cd /var/www/mossbauer.mtholyoke.edu && \
cp -a /mnt/mars/data_Moss ./data_Moss.new && \
chown -R www-data.www-data data_Moss.new && \
rm -r ./data_Moss.old && \
mv ./data_Moss ./data_Moss.old && \
mv ./data_Moss.new ./data_Moss
