# Detect the public IP of the local internet provider changed
   Script /my/path/check_external_ip.sh
   Pre-req : none


# UpdateZoneDNS
Script your DNS update through API and automate them with Cron

for OVH, you need to create API-Key 
    https://www.ovh.com/auth/api/createToken
     in my case (Europe) https://eu.api.ovh.com/createToken/.
    the interface will provide : application_key ,  application_secret  , consumer_key
    depending OVH zone you are, you also need endpoint (in my case "ovh-eu")

for WIX, you also need an API-Key,
     https://manage.wix.com/account/api-keys
      you should see your ACCOUNT_ID
      Create an API Key, result is an AUTH_TOKEN
    
# Pre-reqs
    I use Python to update the Domains and msmtp to send a quick simple email
    sudo yum install pip msmtp
    sudo pip install ovh
    be sure to correctly be able to send email
      1) configure your ~/.msmtprc (this is where your msmtp smtp server parameters are stored) 
      2) test & debut it # echo -e "Subject: Test\n\nthis is an email to test my msmtp SSL config, \n\nAll the best." | msmtp --debug -a myEmailServer my.email@address.com
    My choice :  1 python script.py per domain to update
    All python scripts are called by the check_external_ip.sh script called by CRON every 30mn (*/30 * * * * /my/path/check_external_ip.sh)

HOPE that helps
