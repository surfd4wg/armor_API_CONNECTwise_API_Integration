#!/usr/bin/python3 
"""
# AUTHOR: Craig Ellrod, Cloud Security Architect
# Module documentation.
# Run python3 script CONNECTwise_get_accounts_list_and_addresses.py 
# Input parameters: companyId, clientId, publicKey, privateKey
# Input example: ./CONNECTwise_get_accounts_list_and_addresses.py -coId testcompany_a -clId XXXXXXXX-XXXX-XXXX-b7fd-XXXXXXXXXXXX -pub publicKey pri privateKey
# Output:
#  -> Create a JSON file named "_response_get_CONNECTwise_accounts_and_addresses.json"
# Output Contents:
#  -> JSON file contains a list of companyies in CONNECTwise that belong to the clientId, companyId, publicKey and privateKey
"""

# Imports
import argparse
import requests
import json
import codecs
import base64

# Global variables
null=None
nothing=None

# Class declarations
class CONNECTwise_get_cos:
    def __init__(self, clientId, ENC_AUTH_CODE):
        self.cw_base_url = "https://staging.connectwisedev.com/v4_6_release/apis/3.0"
        self.cw_endpoint_url = "/company/companies/"
        self.ENC_AUTH_CODE=ENC_AUTH_CODE
        self.s="Basic "+codecs.decode(self.ENC_AUTH_CODE, 'UTF-8')
        self.clientId=clientId
        self.connectwise_session = requests.Session()

    def GET_company_companies(self):
        self.method='GET'
        self.cw_full_url = self.cw_base_url + self.cw_endpoint_url
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': self.s,
            'clientId': self.clientId
        }

        try:
            response = requests.get(self.cw_full_url, headers=self.headers, timeout=3)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as errh:
            print ("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else", err)

class CONNECTwise_auth_code():
    def __init__(self, coId, clId, pub, pri):
        self.clientId=clId
        self.companyId=coId
        self.publicAPIKey=pub
        self.privateAPIKey=pri

    def get_auth_code(self):
        AUTH_CODE = (self.companyId+"+"+self.publicAPIKey+":"+self.privateAPIKey)
        encodedAUTH_CODE = base64.b64encode(str.encode(AUTH_CODE))
        decodedAUTH_CODE = base64.b64decode(encodedAUTH_CODE)
        self.encodedAUTH_CODE=encodedAUTH_CODE   
        return AUTH_CODE, encodedAUTH_CODE

def export_to_json(data, outfile):
    json_output=(json.dumps(data, indent=2, separators=(',', ': '), sort_keys=True))
    open(outfile, 'wb').write(bytes(json_output, encoding='utf-8'))

def main(args):
    api_args={
        "coId": args.companyId,
        "clId": args.clientId,
        "pub": args.publicKey,
        "pri": args.privateKey 
    }
    clientId=args.clientId
    AUTH_CODE, encodedAUTH_CODE=CONNECTwise_auth_code(**api_args).get_auth_code()
    response_get_CONNECTwise_company_companies = CONNECTwise_get_cos(clientId, encodedAUTH_CODE).GET_company_companies()
    outfile = '_response_get_CONNECTwise_accounts_addresses.json'

    if outfile:
        print('OUTPUT filename: ', outfile)
        export_to_json(response_get_CONNECTwise_company_companies, outfile)
    else:
        print(response_get_CONNECTwise_company_companies)

# Main body
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-coId", "--companyId", help="CONNECTwise companyId='testcompany_a'")
    parser.add_argument("-clId", "--clientId", help="CONNECTwiseclientId='XXXXXXXX-XXXX-XXXX-b7fd-XXXXXXXXXXXX'")
    parser.add_argument("-pub", "--publicKey", help="CONNECTwise account public key")
    parser.add_argument("-pri", "--privateKey", help="CONNECTwise account private key")
    args = parser.parse_args()
    main(args)
