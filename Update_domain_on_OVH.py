
# Provided in march 2025 by Luc PIERSON <luc.pierson@sdbinfo.fr>
# No Copyright, no guarantee, but currently in production 
# for free use or for example or traning purpose


import ovh
import json
import time

# Config API -- OVH
OVH_CLIENT = ovh.Client(
    endpoint="ovh-eu", 
    application_key="xxxxxxxxxxxxxxxx",
    application_secret="yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
    consumer_key="zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"

)

# define domaine to update and IP Files
DOMAIN_NAME = "mydomain.com"
IP_FILE_PATH = "/my/path/check_current_ip.txt"
OLD_IP_FILE_PATH = "/my/path/check_old_ip.txt"


def read_ip_from_file(file_path):
    """reads IP in file."""
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except Exception as e:
        print(f"❌ Error : Cant read file {file_path} ({e})")
        return None

def get_ovh_user_info():
    """Récupère le prénom et le nom de l'utilisateur OVH."""
    user_data = OVH_CLIENT.get("/me")
    if user_data:
        return user_data.get("firstname", "Unknown"), user_data.get("name", "Unknown")
    return "Unknown_firstname", "Unknown_name"


def get_dns_records():
    """Get A Records of the domain."""
    try:
        return OVH_CLIENT.get(f"/domain/zone/{DOMAIN_NAME}/record", fieldType="A")
    except Exception as e:
        print(f"❌ Error while getting DNS records : {e}")
        return None


def update_dns_record(record_id, new_ip):
    """updates existing DNS record."""
    try:
        OVH_CLIENT.put(f"/domain/zone/{DOMAIN_NAME}/record/{record_id}", target=new_ip)
        print(f"✅  DNS record {record_id} udpated with {new_ip}")
        return True
    except Exception as e:
        print(f"❌ Errour while updating record  {record_id} : {e}")
        return False


def apply_zone_refresh():
    """Apply update at OVH."""
    try:
        OVH_CLIENT.post(f"/domain/zone/{DOMAIN_NAME}/refresh")
        print("🔄 DNS OVH zone refreshed with success.")
    except Exception as e:
        print(f"❌ Error while applying  DNS changes : {e}")


def main():
    first_name, last_name = get_ovh_user_info()
    print(f"👋  =====    Welcome {first_name} {last_name} ! Let's update your DNS records.========  🚀\n")

    """Execute process of DNS Update."""
    print("🔹 Step 1 : get IPs...")

    current_ip = read_ip_from_file(IP_FILE_PATH)
    old_ip = read_ip_from_file(OLD_IP_FILE_PATH)

    if not current_ip or not old_ip:
        return

    print(f"✅ current IP : {current_ip}")
    print(f"✅ old IP : {old_ip}")

    print("🔹 Step 2 : get existing DNS records...")
    records = get_dns_records()
    if not records:
        return

    print(f"✅ {len(records)} A type Records found.")

    updated = False
    for record_id in records:
        record = OVH_CLIENT.get(f"/domain/zone/{DOMAIN_NAME}/record/{record_id}")

        if record["target"] == old_ip:  # Vérification avec l'ancienne IP
            print(f"🔸 update Record  {record['subDomain'] or DOMAIN_NAME} ({record['target']} → {current_ip})")
            if update_dns_record(record_id, current_ip):
                updated = True
        else:
            print(f"⏩ REcord {record['subDomain'] or DOMAIN_NAME} ignored (IP {record['target']} ≠ {old_ip})")

    if updated:
        print("🔹 Step 3 : Apply update...")
        apply_zone_refresh()
    else:
        print("✅ No Update to be done.")


if __name__ == "__main__":
    main()
