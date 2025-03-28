# Provided in march 2025 by Luc PIERSON <luc.pierson@sdbinfo.fr>
# No Copyright, no guarantee, but currently in production 
# for free use or for example or traning purpose



import requests
import os
import json  
import subprocess 



# Change with your Wix identifiers
# https://manage.wix.com/account/api-keys
ACCOUNT_ID = "xxxxxx-xxxx-xxxxx-xxxx-xxxxxxxx"
AUTH_TOKEN = "IST.zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
IP_FILE_PATH = "/my/path/check_current_ip.txt" 
DOMAIN_NAME = "myWixDomain.com"

# URL API Wix DNS 
DNS_API_URL = f"https://www.wixapis.com/domains/v1/dns-zones/{DOMAIN_NAME}"

def get_current_ip(file_path):
    """Read IP in file"""
    try:
        with open(file_path, 'r') as file:
            ip_address = file.read().strip()
            if not ip_address:
                raise ValueError("No IP in the file.")
            print(f"✅ IP in file : {ip_address}")
            return ip_address
    except Exception as e:
        print(f"❌ Error while getting IP in file : {e}")
        return None

def check_domain_exists(domain_name, account_id, auth_token):
    """check if domain exists"""
    curl_command = [
        "curl",
        "-X", "GET",
        DNS_API_URL,
        "-H", f"wix-account-id: {account_id}",
        "-H", f"Authorization: {auth_token}"
    ]

    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        if "dnsZone" in result.stdout:
            print(f"✅ Domain {domain_name} exists and is accessible through the API.")
            return True
        else:
            print(f"❌ Domain {domain_name} not found.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while getting the domain : {e.stderr}")
        return False

def get_dns_info(domain_name, account_id, auth_token):
    """get DNS current informations """
    curl_command = [
        "curl",
        "-X", "GET",
        DNS_API_URL,
        "-H", f"wix-account-id: {account_id}",
        "-H", f"Authorization: {auth_token}"
    ]

    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        dns_info = json.loads(result.stdout)
        print(f"✅ DNS Info provided with success.")
        print(f"🔸 Actual  DNS Informations : {json.dumps(dns_info, indent=2)}")
        return dns_info
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while getting DNS informations : {e.stderr}")
        return None



def update_dns_zone(domain_name, account_id, auth_token, ip_address, dns_info):
    """update DNS records"""
    

    existing_a_record = None
    for record in dns_info['dnsZone']['records']:
        if record['type'] == 'A' and record['hostName'] == domain_name:
            existing_a_record = record
            break
    
    body = {
        "additions": [
            {
                "type": "A",
                "hostName": domain_name,  
                "ttl": 3600,
                "values": [ip_address]
            }
        ],
        "deletions": [],
        "domainName": domain_name
    }

    if existing_a_record:
        body['deletions'].append({
            "type": "A",
            "hostName": domain_name, 
            "values": existing_a_record['values'] 
        })
    
    body_json = json.dumps(body)
    
    curl_command = [
        "curl",
        "-X", "PATCH",
        DNS_API_URL,
        "-H", f"wix-account-id: {account_id}",
        "-H", f"Authorization: {auth_token}",
        "-H", "Content-Type: application/json",
        "-d", body_json
    ]
    
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        print("🔸 JSON DATA sent :")
        print(json.dumps(body, indent=2))
        print(f"🔸 API response : {result.stdout}")
        print("✅ DNS updated with success.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while patching DNS records with API request : {e.stderr}")

def main():
    # Step 1 : Check domain
    if not check_domain_exists(DOMAIN_NAME, ACCOUNT_ID, AUTH_TOKEN):
        return

    # Step 2 : Read IP in file
    ip_address = get_current_ip(IP_FILE_PATH)
    if not ip_address:
        return

    # Step 3 : get actual DNS info
    dns_info = get_dns_info(DOMAIN_NAME, ACCOUNT_ID, AUTH_TOKEN)
    if not dns_info:
        return

    # Step 4 : update  DNS with new IP
    update_dns_zone(DOMAIN_NAME, ACCOUNT_ID, AUTH_TOKEN, ip_address, dns_info)

if __name__ == "__main__":
    main()
