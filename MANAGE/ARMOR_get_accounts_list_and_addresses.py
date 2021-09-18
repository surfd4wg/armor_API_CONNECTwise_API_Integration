#!/usr/bin/python3
"""
# AUTHOR: Craig Ellrod, Cloud Security Architect
# Run python3 script ARMOR_get_accounts_list_and_addresses.py 
# Input parameters: Armor Username, Armor Password, Armor AccountId 
# Run example: ./ARMOR_get_accounts_list_and_addresses.py -u testuser@company.com -p Pa$$w0Rd -a XXXX
# Description: Uses the ARMOR API to pull all master (parent) and sub-accounts (child) for account number XXXX
# # Output: 
# -> creates a JSON file named "_response_get_ARMOR_accounts_addresses.json"
"""
import json
import argparse
import requests
#from requests.models import Response

class OauthTokenRequest:
    def __init__(self, username, password):
        self.base_url = "https://api.armor.com"
        self.auth_data = {
            "username": str(username),
            "password": str(password),
        }
        self.armor_session = requests.Session()

    def get_access_token(self):
        try:
            init_response = self.armor_session.post(
                f"{self.base_url}/auth/authorize", data=self.auth_data
            )
            init_response.raise_for_status()
            auth_code = init_response.json()["code"]
            token_data = {"code": str(auth_code), "grant_type": "authorization_code"}
            response = self.armor_session.post(
                f"{self.base_url}/auth/token", data=token_data
            )
            response.raise_for_status()
            return response.json()["access_token"]
        except requests.exceptions.HTTPError as exc:
            raise SystemExit(exc)

def get_account_list(access_token, account_id):
    url = "https://api.armor.com/accounts"

    headers = {
        "Accept": "application/json",
        "Authorization": f"FH-AUTH {access_token}",
        "X-Account-Context": f"{account_id}",
    }
    parameters = {
        "requestType": "",
        "page": "",
        "maxResults": "",
        "orderBy": "",
        "orderByDirection": ""
    }

    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as exc:
        raise SystemError(exc)

def get_accounts_addresses(accountlist, access_token, account_id):
    company_list=[]
    d={'companies':''}

    tcount=0
    for account in accountlist:
        acct=account['id']
        detailsurl = 'https://api.armor.com/accounts/'+format(acct)
        headers = {
        "Accept": "application/json",
        "Authorization": f"FH-AUTH {access_token}",
        "X-Account-Context": f"{acct}",
            }
        parameters = {
            "requestType": "",
            "page": "",
            "maxResults": "",
            "orderBy": "",
            "orderByDirection": ""
            }

        tcount=tcount+1
        try:
            account_address = requests.get(detailsurl, headers=headers, timeout=3)
            account_address.raise_for_status()
            data=account_address.json()
            account_details={}
            account_details={
                "id": acct,
                "currency": account['currency'],
                "name": account['name'],
                "status": account['status'],
                "parent": account['parent'],
                "products": account['products'],
                "accountType": account['accountType'],
                "isSynced": account['isSynced'],
                "accountId": data['accountId'],
                "addressLine1": data['addressLine1'],
                "addressLine2": data['addressLine2'],
                "city": data['city'],
                "state": data['state'],
                "postalCode": data['postalCode'],
                "country": data['country']
                }

            dictionary_copy=account_details.copy()
            company_list.append([dictionary_copy])
            d.update( {'companies': company_list})

        except requests.exceptions.HTTPError as errh:
            print ("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else", err)

    return d

def export_to_json(data, outfile):
    json_output=(json.dumps(data, indent=2, separators=(',', ': '), sort_keys=True))
    open(outfile, 'wb').write(bytes(json_output, encoding='utf-8'))

def main(args):
    username = args.username
    #password = password = getpass.getpass("Password (No Echo): ")
    password = args.password
    account_id = args.account_id
    access_token = OauthTokenRequest(username,password).get_access_token()
    api_args = {"access_token": str(access_token),"account_id": str(account_id)}
    result = get_account_list(**api_args)
    result2 = get_accounts_addresses(result, **api_args)
    outfile='_response_get_ARMOR_accounts_addresses.json'
    if outfile:
        print('OUTPUT filename: ', outfile)
        export_to_json(result2, outfile)
    else:
        print(result2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="Armor account user name")
    parser.add_argument("-a", "--account_id", help="Armor client account id")
    parser.add_argument("-p", "--password", help="Armor account password")
    parser.add_argument("-o", "--outfile", help="Path to save output json file to")
    args = parser.parse_args()
    main(args)
