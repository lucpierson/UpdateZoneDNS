
# Provided in march 2025 by Luc PIERSON <luc.pierson@sdbinfo.fr>
# No Copyright, no guarantee, but currently in production 
# for free use or for example or traning purpose

import requests
import sys
import json
import os
from datetime import datetime


# API_KEY is the prefix.secret
IONOS_API_KEY = "prefix_value.tocken_value"
DOMAIN = "mydomain.com"
RECORD_TYPE = "A"  
EMAIL_DEST = "contact@mydomain.com"
IP_FILE = "/my/path/check_current_ip.txt"
OLD_IP_FILE = "/my/path/check_old_ip.txt"


HEADERS = {
    "X-API-Key": IONOS_API_KEY,
    "Content-Type": "application/json"
}


mail_buffer = []

def log_message(message):
    """Ajoute un message au tampon et l'affiche."""
    print(message)
    mail_buffer.append(message)

def get_dns_records():
    """get the full list of DNS records of the domain."""
    url = "https://api.hosting.ionos.com/dns/v1/zones"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        zones = response.json()  

        for zone in zones:
            if zone["name"] == DOMAIN:
                zone_id = zone["id"]
                log_message(f"✔ Zone DNS found for {DOMAIN} (ID: {zone_id})")

                records_url = f"https://api.hosting.ionos.com/dns/v1/zones/{zone_id}"
                records_response = requests.get(records_url, headers=HEADERS)

                if records_response.status_code == 200:
                    return zone_id, records_response.json()["records"]

    log_message("⚠ Impossible to get DNS records.")
    return None, []

def get_current_ip():
    try:
        with open(IP_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def get_old_ip():
    try:
        with open(OLD_IP_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def update_dns_record(zone_id, record_id, new_ip, ttl=300):
    """Update DNS record."""
    url = f"https://api.hosting.ionos.com/dns/v1/zones/{zone_id}/records/{record_id}"
    payload = {"content": new_ip, "ttl": ttl}

    response = requests.put(url, headers=HEADERS, data=json.dumps(payload))

    if response.status_code == 200:
        log_message(f"✅ DNS updated ({DOMAIN} -> {new_ip})")
    else:
        log_message(f"⚠ Error while updating DNS : {response.text}")

def send_email():
    """sent content email."""
    log_message("📤 ...")
    email_subject = f"[Alert] Change IP {DOMAIN} : {get_current_ip()}"
    email_body = "\n".join(mail_buffer)

    os.system(f'echo -e "Subject: {email_subject}\n\n{email_body}" | msmtp -a myEmailServer -t {EMAIL_DEST}')

def main():
    """Execute update if required."""
    log_message("\n🔹 start update on  IONOS")

    new_ip = get_current_ip()
    old_ip = get_old_ip()

    if not new_ip:
        log_message("⚠ Impossible to read new IP.")
        send_email()
        sys.exit(1)

    if new_ip == old_ip:
        log_message(f"✔  no update needed, IP is already {new_ip}.")
        send_email()
        sys.exit(0)


    zone_id, records = get_dns_records()
    if not records:
        send_email()
        sys.exit(1)


    for record in records:
        if record["type"] == "A" and record["name"] == DOMAIN and record["content"] == old_ip:
            log_message(f"🔹 Enregistrement trouvé : {record}")
            update_dns_record(zone_id, record["id"], new_ip, record["ttl"])


    send_email()

if __name__ == "__main__":
    main()


