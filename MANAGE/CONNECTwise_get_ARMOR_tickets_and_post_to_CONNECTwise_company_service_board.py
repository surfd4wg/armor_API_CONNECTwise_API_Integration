#!/usr/bin/python3 
"""
# AUTHOR: Craig Ellrod, Cloud Security Architect
# Run Python3 script CONNECTwise_get_ARMOR_tickets_and_post_to_CONNECTwise_company_service_board.py
# Description: Uses the ARMOR json response file produced in the previous step as input, Reads the ARMOR account Id from the file,
# finds the matching company in CONNECTwise company, custom field ARMORcompanyId, takes that CONNECTwise company information
# and posts the tickets from the ARMOR file, into the CONNECTwise company's default service board.
# Input parameters: 
#   CONNECTwise companyId, 
#   CONNECTwise clientId, 
#   CONNECTwise publicKey, 
#   CONNECTwise privateKey,
#   ARMOR Tickets Input File,
#   CONNECTwise Service Board (to post the ARMOR tickets to)
# Run example: ./CONNECTwise_get_ARMOR_tickets_and_post_to_CONNECTwise_company_service_board.py \
#   -coId testcompany_a \
#   -clId XXXXXXXX-XXXX-XXXX-b7fd-XXXXXXXXXXXX \
#   -pub publicKey \
#   -pri privateKey \
#   -inFile "_response_GET_ARMOR_tickets_for_account_XXXX.json"
#   -SvcBoard "ARMIORtickets"
# Output:
#  -> Creates a JSON file named "_response_post_CONNECTwise_service_tickets_from_ARMOR_account_XXXX_(CompanyIdentifer).json"
#  -> Where XXXX equals the ARMOR AccountId, CompanyIdentifer is the matching Identifier in CONNECTwise
"""

# Imports
import os
import sys
import argparse
import requests
import logging
import json

import hidden
import codecs
import base64
import urllib.parse
import attr
import datetime 
from json import JSONEncoder, dumps
from typing import TypeVar
from typing import AnyStr


# Global variables
avar=None
null=None

# Class declarations
class CONNECTwise_get_service_board:
    def __init__(self, clId, ENC_AUTH_CODE, ServiceBoardName):
        #print('CONNECTwise __init__')
        self.cw_base_url = "https://staging.connectwisedev.com/v4_6_release/apis/3.0"
        self.cw_endpoint_url = "/service/boards/"
        self.cw_serviceBoard=ServiceBoardName
        d={}
        self.cw_query_string="name like \'"+self.cw_serviceBoard+"\'"
        d['conditions'] = self.cw_query_string
        #print('d: ', d)
        urltest="?"+urllib.parse.urlencode(d)
        #print('urltest: ', urltest)
        #innk=input('press')
        
        #cw_dic={ self.cw_query_string }
        #print('cw_dic: ', cw_dic)
        #keyinput=input('press any key')
        #self.cw_dict = { 'conditions': 'name line '+ ="ARMORcompanyId" AND value = '+str(acct)}
        self.cw_queryString = "?" + urllib.parse.urlencode(d)
        self.cw_full_url = self.cw_base_url + self.cw_endpoint_url + self.cw_queryString
        self.cw_query = { "conditions": "name like 'ARMORtickets'"}
        self.cw_queryString = "?" + urllib.parse.urlencode(self.cw_query)
 
        self.clientId=clId
        self.ENC_AUTH_CODE=ENC_AUTH_CODE
        self.s="Basic "+codecs.decode(self.ENC_AUTH_CODE, 'UTF-8')
        self.cw_query = { "conditions": "name like 'ARMORtickets'"}
        self.cw_queryString = "?" + urllib.parse.urlencode(self.cw_query)
        urltestfull=self.cw_base_url + self.cw_endpoint_url +  urltest
        self.cw_full_url = self.cw_base_url + self.cw_endpoint_url + urltest
        #print('urltestfull: ', urltestfull)
        #print('cw full query string service board: ', self.cw_full_url)
        #ink=input('press any key')
        self.connectwise_session = requests.Session()

    def GET_CONNECTwise_serviceBoard(self):
        self.method='GET'
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

class CONNECTwise_get_company_byArmorId:
    def __init__(self, clId, ENC_AUTH_CODE, ARMORacctId):
        self.cw_dict={}
        #acct=7777
        acct=ARMORacctId
        self.ENC_AUTH_CODE=ENC_AUTH_CODE
        self.cw_base_url = "https://staging.connectwisedev.com/v4_6_release/apis/3.0"
        self.cw_endpoint_url = "/company/companies/"
        self.cw_dict = { 'conditions': 'customFieldConditions=caption="ARMORcompanyId" AND value = '+str(acct)}
        self.cond_query = 'conditions: '
        self.custom_query = 'customFieldConditions=caption="ARMORcompanyId"'
        self.custom_and=' AND value = '+urllib.parse.quote(str(acct))
        self.cw_query=self.custom_query+self.custom_and
        self.cw_queryString = "?" + self.cw_query
        self.cw_full_url = self.cw_base_url + self.cw_endpoint_url + self.cw_queryString
        self.clientId=clId
        self.s="Basic "+codecs.decode(self.ENC_AUTH_CODE, 'UTF-8')
        self.connectwise_session = requests.Session()

    def GET_company_byArmorId(self):
        self.method='GET'
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

class CONNECTwise_post_tickets():
    def __init__(self, clientId, ENC_AUTH_CODE, inputFile, inputBoard):
        #print('CONNECTwise __init__')
        self.cw_base_url = "https://staging.connectwisedev.com/v4_6_release/apis/3.0"
        self.cw_endpoint_url = "/service/tickets/"

        self.inputFile=inputFile
        self.inputBoard=inputBoard
        self.clientId=clientId
        self.encodedAUTH_CODE=ENC_AUTH_CODE
        self.s="Basic "+codecs.decode(self.encodedAUTH_CODE, 'UTF-8')
        self.connectwise_session = requests.Session()

    def post_CONNECTwise_company_service_tickets(self):
        #print('post_CONNECTwise_company_service_tickets')
        # These two lines enable debugging at httplib level (requests->urllib3->http.client)
        # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
        # The only thing missing will be the response.body which is not logged.
        #try:
        #    import http.client as http_client
        #    from http.client import HTTPConnection
        #except ImportError:
        #   import httplib as http_client
        #http_client.HTTPConnection.debuglevel = 1

        # You must initialize logging, otherwise you'll not see debug output.
        #logging.basicConfig()
        #logging.getLogger().setLevel(logging.DEBUG)
        #requests_log = logging.getLogger("requests.packages.urllib3")
        #requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = True

        #requests.get('https://httpbin.org/headers')
        self.method='POST'
        self.cw_full_url = self.cw_base_url + self.cw_endpoint_url
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': self.s,
            'clientId': self.clientId
        }
        #self.params = {
        #    'clientId': self.clientId
        #}
        cw_data = {}

        # Armor Tickets Loop
        ticketfile=self.inputFile
        with open(ticketfile) as json_file:
            ticket_list = json.load(json_file)
            #print('ticket list type: ', type(ticket_list))
            var1 = ticket_list
            #print("My variable of interest is {}".format(var1))
            
            ArmorAcctId=ticket_list['id']
            print('\r\nGetting tickets for Armor AccountId: ', ArmorAcctId)
            #print('Armor acct id: ', ArmorAcctId)
            CONNECTwise_companyId = CONNECTwise_get_company_byArmorId(self.clientId, self.encodedAUTH_CODE, ArmorAcctId).GET_company_byArmorId()
            #print('CONNECTwise companyId: ', CONNECTwise_companyId)
            clist=json.dumps(CONNECTwise_companyId)
            #print('clist: ', type(clist), clist)
            cson_output=(json.dumps(CONNECTwise_companyId, indent=2, separators=(',', ': '), sort_keys=True))
            cson_data=json.loads(cson_output)
            #print('cson_data: ', type(cson_data), cson_data)
            #print('cson_output: ', type(cson_output), cson_output)
            companyId=CONNECTwise_companyId
            
            #keyinput=input('press any key')
            clist=cson_data
            #print('clist: ', type(clist), clist)
            #ink=input('press any key')
            for cdic in clist:
                #print('cdic: ', type(cdic), cdic)
                #print('cdic id: ', type(cdic['id']), cdic['id'])
                companyId=cdic['id']
                companyIdentifier=cdic['identifier']
                companyIdName=cdic['name']
                #print('company ....: ', companyId, companyIdentifier, companyIdName)
                #ink=input('press any key')

            print('\r\nAdding tickets from Armor to Connectwise CompanyId: ', companyId, companyIdName, end='', flush=True)
            CONNECTwise_serviceBoard = CONNECTwise_get_service_board(self.clientId, self.encodedAUTH_CODE, self.inputBoard).GET_CONNECTwise_serviceBoard()
            #print('CONNECTwise_serviceBoard: ', CONNECTwise_serviceBoard)
            blist=json.dumps(CONNECTwise_serviceBoard)
            #print('blist: ', type(blist), blist)
            #keyinput=input('press any key')
            #serviceBoardId=CONNECTwise_serviceBoard['id']
            #serviceBoardIdName=CONNECTwise_serviceBoard['name']
            
            json_output=(json.dumps(CONNECTwise_serviceBoard, indent=2, separators=(',', ': '), sort_keys=True))
            json_data = json.loads(json_output)
            #print('json_data: ', type(json_data), json_data)
            #print('json_output: ', type(json_output), json_output)

            blist=json_data
            #print('blist: ', type(blist), blist)
            #ink=input('press any key')
            for bdic in blist:
                #print('bdic: ', type(bdic), bdic)
                #print('bdic id: ', type(bdic['id']), bdic['id'])
                serviceBoardId=bdic['id']
                serviceBoardIdName=bdic['name']
                #ink=input('press any key')
                #for b:
                    #brd=bkey['id']
                    #print('bkey: ', type(bkey), bkey)
                    #ink=input('press any key')
            
            #print('range, len of ticket_list: ', range(len(ticket_list)))
            #print('range, len of ticket_list: ', range(len(ticket_list['tickets'])))

            #key_pressed = input('Press ENTER to continue: ')
            tlist=ticket_list['tickets']
            #print('tlist type: ', type(tlist))
            #print('tlist: ', tlist)
            #key_pressed = input('Press ENTER to continue: ')
            tcount=0
            for dic in tlist:
                #print('dic: ', dic)
                for key in dic:
                    tcount=tcount+1
                    sliced=key['ticketNumber']
                    diced=sliced[4:]
                    chopped=int(diced)
                    comment_string=key['ticketComment']
                    comment_string=comment_string.replace("\n"," ").replace("\r\n", " ").replace("\r", " ")
                    desc_string=key['ticketDescription']
                    desc_string=desc_string.replace("\n"," ").replace("\r\n", " ").replace("\r", " ")
                    ticket_url="https://support.armor.com/servicedesk/customer/portal/6/"+key['ticketNumber']
                    print('\r\bGetting ARMOR Ticket Number: ', key['ticketNumber'], ' ', end='', flush=True)
                    #print('types: ', type(comment_string), type(desc_string))
                    #print ('dic[key]: ', key)
                    #print ('dic key ticketNumber: ', chopped)
                    #print ('dic key ticketDescription ', desc_string)
                    #print ('dic key ticketComment ', comment_string)
                    #print ('dic key summary: ', key['summary'])
                    #print ('dic key requestTypeId ', key['requestTypeId'])
                    #print ('dic key requestTypeName ', key['requestTypeName'])
                    ##print ('dic key descriptionCreationDate: ', key['descriptionCreationDate'])
                    #print ('dic key commentCreationDate', key['commentCreationDate'])
                    #print ('dic key currentStatus ', key['currentStatus'])
                    ticket_dict={'connectwiseTicketNumber': chopped,
                        'currentStatus': key['currentStatus'],
                        'requestTypeId': key['requestTypeId'],
                        'requestTypeName': key['requestTypeName'],
                        'summary': key['summary'],
                        'ticketDescription': desc_string,
                        'descriptionCreationDate':key['descriptionCreationDate'],
                        'ticketComment':  comment_string,
                        'commentCreationDate': key['commentCreationDate'],
                        'armorTicketNumber': key['ticketNumber']}
                    #print('ticket_dict type: ', type(ticket_dict))
                    #print('ticket dict: ', ticket_dict)
                    #json_data = json.load(data)
                    json_output=(json.dumps(ticket_dict, indent=2, separators=(',', ': '), sort_keys=True))
                    #print('json_output: ', json_output)
                    outfile="_connectwise_ticket_"+str(tcount)+".json"
                    open(outfile, 'wb').write(bytes(json_output, encoding='utf-8'))
                    summary=key['summary']
                    summary100 = summary[0:100]
                    a_datetime = datetime.datetime.now()
                    formatted_datetime = a_datetime.isoformat()
                    json_datetime = json.dumps(formatted_datetime)

                    self.cw_POST_data={
                        "id": chopped,
                        "summary": summary100,
                        "recordType": 'ServiceTicket',
                        "initialDescription": ticket_url +" "+desc_string,
 
                        "board": {
                            "id": serviceBoardId,
                            "name": serviceBoardIdName,
                        },
                        "status": {
                            "id": null,
                            "name": key['currentStatus'],
                        },
                        "company": {
                            "id": companyId,
                            "identifier": companyIdentifier,
                            "name": companyIdName,
                        },
                        "priority": {
                            "id": 0,
                            "name": "string",
                            "sort": 0,
                        },
                        "source": {
                            "id": 3,
                            "name": "ARMOR Defense, Inc"    
                        }
                    }
                    json_output=(json.dumps(self.cw_POST_data, indent=2, separators=(',', ': '), sort_keys=True))
                    #print('json_output: ', json_output)
                    outfile="_response_post_CONNECTwise_service_tickets_from_ARMOR_account_"+str(ArmorAcctId)+"_"+companyIdentifier+".json"
                    open(outfile, 'ab').write(bytes(json_output, encoding='utf-8'))
                    open(outfile, 'ab').write(bytes(',\n', encoding='utf-8'))
                    #print('self.cw_data type: ', type(self.cw_POST_data))
                    #print('self.cw_data: ', self.cw_POST_data)

                    try:
                        response = requests.post(self.cw_full_url, headers=self.headers, data=json.dumps(self.cw_POST_data), timeout=3)
                        ###########print('\r\n&&&&&&&&&&&& BOARD POST &&&&&&&&&&&&&')
                        #print('response type: ', type(response))
                        #print('response: ', response)
                        
                        a = json.loads(response.content)
                        #print(a['id'])
                        print('Created CONNECTwise Ticket: ', a['id'], '\r\n', end='', flush=True)
                        #print('response headers: ', response.headers)
                        #print('reesponse json: ', response.json)
                        #print('response raw: ', response.raw)
                        response.raise_for_status()

                    except requests.exceptions.HTTPError as errh:
                        print ("Http Error:", errh)
                    except requests.exceptions.ConnectionError as errc:
                        print ("Error Connecting:", errc)
                    except requests.exceptions.Timeout as errt:
                        print ("Timeout Error:", errt)
                    except requests.exceptions.RequestException as err:
                        print ("OOps: Something Else", err)

        return outfile

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
    #print('main:')
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

    api_args={
        "coId": args.companyId,
        "clId": args.clientId,
        "pub": args.publicKey,
        "pri": args.privateKey
    }
    clientId=args.clientId
    inputFile=args.inputFile
    inputBoard=args.serviceBoard
    #ARMORid=5594
    AUTH_CODE, encodedAUTH_CODE=CONNECTwise_auth_code(**api_args).get_auth_code()
    
    ##print('response type: ', type(response_get_CONNECTwise_company_byArmorId))
    #print('response:  ', response_get_CONNECTwise_company_byArmorId)
    response_post_CONNECTwise_service_tickets = CONNECTwise_post_tickets(clientId, encodedAUTH_CODE, inputFile, inputBoard).post_CONNECTwise_company_service_tickets()
    #print('CONNECTwise service tickets: ', CONNECTwise_service_tickets)
    outfile = response_post_CONNECTwise_service_tickets

    if outfile:
        print('\r\nOUTPUT filename: ', outfile)
        print('\r\n')
        #export_to_json(response_get_CONNECTwise_company_byArmorId, outfile)
    #else:
    #    print(response_get_CONNECTwise_company_byArmorId)

# Main body
if __name__ == '__main__':
    #print('__name__: ', __name__)
    parser = argparse.ArgumentParser()
    parser.add_argument("-coId", "--companyId", help="CONNECTwise companyId='testcompany_a'")
    parser.add_argument("-clId", "--clientId", help="CONNECTwiseclientId='XXXXXXXX-XXXX-XXXX-b7fd-XXXXXXXXXXXX'")
    parser.add_argument("-pub", "--publicKey", help="CONNECTwise account public key")
    parser.add_argument("-pri", "--privateKey", help="CONNECTwise account private key")
    parser.add_argument("-inFile", "--inputFile", help="ARMOR ticket file as input")
    parser.add_argument("-svcBoard", "--serviceBoard", help="CONNECTwise service board to place ARMOR tickets into")
    args = parser.parse_args()
    main(args)
