#!/usr/bin/python3
"""
# AUTHOR: Craig Ellrod, Cloud Security Architect
# Run Python3 script ARMOR_get_tickets_for_account.py
# Description: Uses the ARMOR API to pull all tickets (50 at a time) from ARMOR for the specified account XXXX
# Input parameters: Armor Username, Armor Password, Armor AccountId 
# Run example: ./ARMOR_get_tickets_for_account.py -u testuser@company.com -p Pa$$w0Rd -a XXXX
# Output:
# -> Creates a JSON file named "_response_get_ARMOR_tickets_for_account_XXXX.json 
"""
import json
import time
import sys
import argparse
import logging
import requests
from requests.models import Response


class OauthTokenRequest:
    def __init__(self, username, password):
        self.base_url = "https://api.armor.com"
        self.auth_data = {
            "username": str(username),
            "password": str(password),
        }
        self.armor_session = requests.Session()

    def get_access_token(self):
        # Request auth access token
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

def get_ticket_list(access_token, account_id):
    url = "https://api.armor.com/tickets/list"
    headers = {
        "Accept": "application/json",
        "Authorization": f"FH-AUTH {access_token}",
        "X-Account-Context": f"{account_id}",
    }
    params = {
        "requestType": "",
        "page": "",
        "maxResults": "",
        "orderBy": "",
        "orderByDirection": ""
    }

    payload = json.dumps(params, indent=4)

    try:
        response = requests.get(url, headers=headers, params=payload)
        return response.json()

    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)

def get_ticket_details(ticketlist, access_token, account_id ):

    a_list=[]
    d={'tickets':[]}

    print('\r\nGetting tickets for Armor account id: '+str(account_id)+'\r\n')
    
    for ticket in ticketlist['items']:
        print('.', end='', flush=True)
        t=ticket['issueKeyId']
        detailsurl = 'https://api.armor.com/tickets/'+format(t)+'/details'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'FH-AUTH {access_token}',
            'X-Account-Context': f'{account_id}',
            }
        parameters = {
            'requestType': '',
            'page': '',
            'maxResults': '',
            'orderBy': '',
            'orderByDirection': ''
            }
        #parameters = json.dumps(parameters, indent=4)
        try:
            get_details = requests.get(detailsurl, headers=headers, params=parameters, timeout=3)
            get_details.raise_for_status()
            ticket_details=get_details.json()
                
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)

        try:
            commenturl = 'https://api.armor.com/tickets/'+format(t)+'/comments'
            get_comments = requests.get(commenturl, headers=headers, params=parameters, timeout=3)
            get_comments.raise_for_status()
            ticket_comments=get_comments.json()

        except requests.exceptions.HTTPError as errh:
            print ("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else", err)

        for k, v in ticket_comments.items():
            if isinstance(v, list):
                for j in v:
                    jkeys=list(j.keys())
                    if 'comment' in jkeys:
                        jcomment=""
                        jcomment=j['comment']
                        jdate=j['createdDate']

                    else:
                        break
            else:
                continue
        #keys=ticket_comments.keys()

        ticket_dict={'ticketNumber': ticket['issueKeyId'],
            'currentStatus': ticket['currentStatus'],
            'requestTypeId': ticket['requestType']['id'],
            'requestTypeName': ticket['requestType']['name'],
            'summary': ticket['summary'],
            'ticketDescription': ticket_details['description'],
            'descriptionCreationDate': ticket_details['createdDate'],
            'ticketComment': jcomment,
            'commentCreationDate': jdate}
        dictionary_copy=ticket_dict.copy()
        a_list.append([dictionary_copy])
        d.update( {'tickets': a_list})

    return d

def get_ticket_comments(ticket, access_token, account_id ):
    t=ticket
    commenturl = 'https://api.armor.com/tickets/'+format(t)+'/comments'
    print('COMMENT URL: ', commenturl)
    headers = {
        'Accept': 'application/json',
        'Authorization': f'FH-AUTH {access_token}',
        'X-Account-Context': f'{account_id}',
    }
    parameters = {
        'requestType': '',
        'page': '',
        'maxResults': '',
        'orderBy': '',
        'orderByDirection': ''
    }
    #parameters = json.dumps(parameters, indent=4)
    try:
        response = requests.get(commenturl, headers=headers, params=parameters, timeout=3)
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

def append_tickets_to_accountId(account, ticketdic):
    dest={}
    acct=account
    ticketsAcct={}
    ticketsAcct={'id': acct}
    dest.update(ticketsAcct)
    dest.update(ticketdic)
    d=dest

    return d

def export_to_json(data, outfile):
    json_output=(json.dumps(data, indent=2, separators=(',', ': '), sort_keys=True))
    open(outfile, 'wb').write(bytes(json_output, encoding='utf-8'))

def main(args):
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

    username = args.username
    #password = password = getpass.getpass("Password (No Echo): ")
    password=args.password
    account_id=args.account_id
    ARMOR_access_token = OauthTokenRequest(username,password).get_access_token()
    #api_args = {"access_token": str(ARMOR_access_token),"account_id": str(account_id)}
    ticketlist = get_ticket_list(ARMOR_access_token, account_id)
    ticketdetails = get_ticket_details(ticketlist, ARMOR_access_token, account_id)
    #result = get_ticket_list(**api_args)
    ticketsaccount = append_tickets_to_accountId(account_id, ticketdetails)
    outfile='_response_get_ARMOR_tickets_for_account_'+str(account_id)+'.json'

    #print('result: ', ticketsaccount)
    if outfile:
        print('\r\nOUTPUT filename: ', outfile)
        export_to_json(ticketsaccount, outfile)
    else:
        print(ticketsaccount)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="Armor account user name")
    parser.add_argument("-p", "--password", help="Armor account password")
    parser.add_argument("-a", "--account_id", help="Armor client account id")
    parser.add_argument("-o", "--outfile", help="Path to save output json file to")
    args = parser.parse_args()
    main(args)
