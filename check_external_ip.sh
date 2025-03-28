#!/bin/bash


# Provided in march 2025 by Luc PIERSON <luc.pierson@sdbinfo.fr>
# No Copyright, no guarantee, but currently in production 
# for free use or for example or traning purpose


# files to store IPs
IP_FILE="/my/path/check_current_ip.txt"
IP_FILE_OLD="/my/path/check_old_ip.txt"
#  e-mail to send change alert
EMAIL=" my.email@address.com"
DATE_TIME=$(date +"%Y-%m-%d  %H:%M")


# get public IP of the internet provider box
CURRENT_IP=$(curl -s https://checkip.ovh/ | grep -oP '(?<=<p class="h5 alert alert-success">)[0-9\.]+')
#CURRENT_IP=$(curl -s https://ifconfig.me)

# check file
if [[ -f "$IP_FILE" ]]; then
    OLD_IP=$(cat "$IP_FILE")
else
    OLD_IP=""
fi

# Compare IPs
if [[ "$CURRENT_IP" != "$OLD_IP" ]]; then
    mv $IP_FILE $IP_FILE_OLD
    echo "$CURRENT_IP" > "$IP_FILE" 
    MAIL_CONTENT="New IP on Internet BOX: $CURRENT_IP"


    echo -e "Subject: $DATE_TIME [Alert] Change IP on Internet Box : $CURRENT_IP \n\n $MAIL_CONTENT" | msmtp -t $EMAIL
    python /my/path/Update_domain_on_WIX.py
    python /my/path/Update_domain_on_OVH.py
fi

