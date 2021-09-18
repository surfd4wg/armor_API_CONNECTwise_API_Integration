#!/usr/bin/python3
"""
# AUTHOR: Craig Ellrod, Cloud Security Architect
# Run python3 script ARMOR_match_and_update_CONNECTwise_company_custom_fields.py
# Description: 
# Match the ARMOR accounts in "_response_get_ARMOR_accounts_addresses.json" with 
#  CONNECTwise companies in "_response_get_CONNECTwise_accounts_and_addresses.json"
#  and UPDATES those companies in CONNECTwise with ARMOR custom field information.
# Input parameters: companyId, clientId, publicKey, privateKey
# Run example: ./ARMOR_match_and_update_CONNECTwise_company_custom_fields.py -coId testcompany_a -clId XXXXXXXX-XXXX-XXXX-b7fd-XXXXXXXXXXXX -pub publicKey pri privateKey
# Fields that will be updated in CONNECTwise Company Overview are:
#  -ARMORcompanyId - a four digit integer identifying the account id in the Armor Management Portal
#  -ARMORcompanyName - a string identifying the account name in the Armor Management Portal
#  -ARMORparentId - a four digit integer identifying the account's parent account id in the Armor Management Portal
#  -ARMORdateUpdated - a date in ISO-8601 format that this update happened
# Output:
#  -> Create a filename for each record updated in CONNECTwise, for example _response_update_CONNECTwise_company_custom_fields_(id)_(name).JSON
"""
import json
import argparse
import requests
import base64
import codecs 
import urllib.parse
import datetime
from requests.models import Response
from datetime import timezone

class CONNECTwise_update_company_byName:
    def __init__(self, clientId, ENC_AUTH_CODE):
        self.cw_base_url = "https://staging.connectwisedev.com/v4_6_release/apis/3.0"
        self.ENC_AUTH_CODE=ENC_AUTH_CODE
        self.s="Basic "+codecs.decode(self.ENC_AUTH_CODE, 'UTF-8')
        self.clientId=clientId
        self.connectwise_session = requests.Session()
        self.cw_PATH_data={}

    def patch_ARMOR_to_CONNECTwise_company_custom_fields(self, ARMORid, ARMORname, ARMORparent, CONNECTwiseCompanyId, CONNECTwiseCompanyName):
        aId=ARMORid
        aName=ARMORname
        aParent=ARMORparent
        cId=CONNECTwiseCompanyId
        cName=CONNECTwiseCompanyName
        a_datetime = datetime.datetime.now()
        formatted_datetime = a_datetime.isoformat()
        json_datetime = json.dumps(formatted_datetime)
        ztime=a_datetime.astimezone(timezone.utc).replace(tzinfo=None).isoformat(timespec='milliseconds') + 'Z'
        self.cw_endpoint_url = "/company/companies/"+str(cId)
        self.cw_full_url = self.cw_base_url + self.cw_endpoint_url
        self.method='PATCH'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': self.s,
            'id': str(cId),
            'clientId': self.clientId
        }
        self.cw_PATCH_data = [
            {
                "op": "replace",
                "path": "customFields",
                "value": [
                    {
                    "caption": "ARMORcompanyId",
                    "entryMethod": "EntryField",
                    "id": 1,
                    "numberOfDecimals": 0,
                    "type": "Number",
                    "value": aId
                    },
                    {
                    "caption": "ARMORcompanyName",
                    "entryMethod": "EntryField",
                    "id": 2,
                    "numberOfDecimals": 0,
                    "type": "Text",
                    "value": aName
                    },
                    {
                    "caption": "ARMORparentId",
                    "entryMethod": "EntryField",
                    "id": 3,
                    "numberOfDecimals": 0,
                    "type": "Number",
                    "value": aParent
                    },
                    {
                    "caption": "ARMORdateUpdated",
                    "entryMethod": "EntryField",
                    "id": 4,
                    "numberOfDecimals": 0,
                    "type": "Date",
                    "value": ztime
                    }
                ]
            }
        ]       
        
        try:
            response = requests.patch(self.cw_full_url, headers=self.headers, data=json.dumps(self.cw_PATCH_data), timeout=3)
            response.raise_for_status()
            return response, ztime

        except requests.exceptions.HTTPError as errh:
            print ("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else", err)

class CONNECTwise_get_company_byName:
    def __init__(self, clientId, ENC_AUTH_CODE):
        self.cw_base_url = "https://staging.connectwisedev.com/v4_6_release/apis/3.0"
        self.cw_endpoint_url = "/company/companies/"
        self.ENC_AUTH_CODE=ENC_AUTH_CODE
        self.s="Basic "+codecs.decode(self.ENC_AUTH_CODE, 'UTF-8')
        self.clientId=clientId
        self.connectwise_session = requests.Session()

    def GET_company_byName(self, tf, CONNECTwiseCompanyName):
        tf='n'
        self.ccname=CONNECTwiseCompanyName
        self.cw_query = { "conditions": "name like '{self.ccname}'"}
        self.cw_queryString = "?" + urllib.parse.urlencode(self.cw_query)
        self.cw_full_url = self.cw_base_url + self.cw_endpoint_url + self.cw_queryString
        self.method='GET'
        
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': self.s,
            'clientId': self.clientId
        }

        try:
            response = requests.get(self.cw_full_url, headers=self.headers, timeout=3)
            response.raise_for_status()
            return 'y'

        except requests.exceptions.HTTPError as errh:
            print ("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else", err)

class CONNECTwise_match_accounts:
    def __init__(self, clientId, encodedAUTH_CODE):
        self.armor_file='_response_get_ARMOR_accounts_addresses.json'
        self.cw_file='_response_get_CONNECTwise_accounts_addresses.json'
        self.clientId=clientId
        self.encodedAUTH_CODE=encodedAUTH_CODE

    def match_accounts_addresses(self):
        with open(self.armor_file) as armor_json_file:
            companyList = json.load(armor_json_file)
            clist=companyList['companies']
            for armor_dic in clist:
                for key in armor_dic:
                    noSpaces=key['name'].replace(" ", "")
                    tIdstr="5"+str(key['id'])
                    #identifier=str(key['parent'])+"_"+tIdstr+"_"+noSpaces
                    #identifier25=identifier[0:25]
                    co_str=""
                    with open(self.cw_file) as cw_json_file:
                        cwList=json.load(cw_json_file)
                        for cw_dic in cwList:
                            co_str=key['name']
                            cw_str=cw_dic['name']
                            if (cw_str.__contains__(co_str)):
                                print('\r\n----------------------------------\r\n')
                                print('I FOUND a match!\r\n')
                                print('ARMOR company: ', key['name'], "<--> CONNECTwise company: ",cw_dic['name'])
                                
                                #print('armor dictionary: ', armor_dic)
                                print('\r\n  ARMOR company ----------')
                                print('  ARMOR accountId: ', key['accountId'])
                                print('  ARMOR id: ', key['id'])
                                print('  ARMOR name: ', key['name'])
                                print('  ARMOR addressLine1: ', key['addressLine1'])
                                print('  ARMOR addressLine2: ', key['addressLine2'])
                                print('  ARMOR city: ', key['city'])                
                                print('  ARMOR state: ', key['state'])
                                print('  ARMOR postalCode: ', key['postalCode'])
                                
                                #print('CONNECTwise dictionary: ', cw_dic)
                                print('\r\n  CONNECTwise company ----------')
                                print('  CONNECTwise identifier: ', cw_dic['identifier'])
                                print('  CONNECTwise id: ', cw_dic['id'])
                                print('  CONNECTwise name: ', cw_dic['name'])
                                print('  CONNECTwise addressLine1: ', cw_dic['addressLine1'])
                                if cw_dic.__contains__('addressLine2'):
                                    print('  CONNECTwise addressLine2: ', cw_dic['addressLine2'])

                                print('  CONNECTwise city: ', cw_dic['city'])                
                                print('  CONNECTwise state: ', cw_dic['state'])
                                print('  CONNECTwise zip: ', cw_dic['zip'])

                                YorN=ask_user(key['id'],key['name'],key['parent'],cw_dic['id'],cw_dic['name'])

                                if YorN == True:
                                    tf='n'
                                    response_get_CONNECTwise_company_byName = CONNECTwise_get_company_byName(self.clientId, self.encodedAUTH_CODE).GET_company_byName(tf, cw_dic['name'])
                                    if response_get_CONNECTwise_company_byName == 'y':
                                        response_update_CONNECTwise_company_custom_fields, self.ztime = CONNECTwise_update_company_byName(self.clientId, self.encodedAUTH_CODE).patch_ARMOR_to_CONNECTwise_company_custom_fields(key['id'], key['name'], key['parent'], cw_dic['id'], cw_dic['name'])
                                        print('\r\nUpdated CONNECTwise company record with the ARMOR Custom Field information: ')
                                        
                                        print('\r\n  CONNECTwise company id: ', cw_dic['id'])
                                        print('  CONNECTwise company name: ', cw_dic['name'])
                                        print('\r\n  Custom Field ARMORcompanyId: ', key['id'])
                                        print('  Custom Field ARMORcompanyName: ', key['name'])
                                        print('  Custom Field ARMORparentId: ', key['parent'])
                                        print('  Custom Field ARMORdateUpdated: ', self.ztime)
                                        outfile = '_response_update_CONNECTwise_company_custom_fields_'+str(cw_dic['id'])+'_'+cw_dic['identifier']+'.json'
                                        if outfile:
                                            print('  OUTPUT logfile: ', outfile)
                                            export_to_json(cw_dic, outfile)
                                        else:
                                            print(response_update_CONNECTwise_company_custom_fields)
                            else:
                                continue

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

def ask_user(ARMORid, ARMORname, ARMORparent, CONNECTwiseCompanyId, CONNECTwiseCompanyName):
    prompt = " [y/N] "
    print('\r\n----------------------------------')
    print('\r\n  CONNECTwise company id: ', CONNECTwiseCompanyId)
    print('  CONNECTwise company name: ', CONNECTwiseCompanyName)
    print('\r\n  Custom Field ARMORcompanyId: ', ARMORid)
    print('  Custom Field ARMORcompanyName: ', ARMORname)
    print('  Custom Field ARMORparentId: ', ARMORparent)
    question='\r\nWould you like to update the CONNECTwise company record with the ARMOR Custom Field information?'
    while True:
        try:
            resp = input(question + prompt).strip().lower()
            if resp == 'Y' or resp == 'y' or resp =='YES':
                return True
            else:
                return False
        except ValueError:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

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
    
    # Logging for Debugging
    #try:
    #    import http.client as http_client
    #    from http.client import HTTPConnection
    #except ImportError:
    #    import httplib as http_client
    #http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    #logging.basicConfig()
    #logging.getLogger().setLevel(logging.DEBUG)
    #requests_log = logging.getLogger("requests.packages.urllib3")
    #requests_log.setLevel(logging.DEBUG)
    #requests_log.propagate = True

    result=CONNECTwise_match_accounts(clientId, encodedAUTH_CODE).match_accounts_addresses()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-coId", "--companyId", help="CONNECTwise companyId='testcompany_a'")
    parser.add_argument("-clId", "--clientId", help="CONNECTwiseclientId='XXXXXXXX-XXXX-XXXX-b7fd-XXXXXXXXXXXX'")
    parser.add_argument("-pub", "--publicKey", help="CONNECTwise account public key")
    parser.add_argument("-pri", "--privateKey", help="CONNECTwise account private key")
    args = parser.parse_args()
    main(args)
