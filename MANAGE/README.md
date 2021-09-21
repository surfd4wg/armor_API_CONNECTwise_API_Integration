[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

## This Repo

This Repo is intended to be used for integration between ARMOR Cloud Security's APIs and
CONNECTwise's APIs - for use by Managed Service Providers (MSPs). This repo applies
specifically to the CONNECTwise "MANAGE" product.

## This repository contains:

Files in this repo are all Python3 scripts:
1. ARMOR_get_accounts_list_and_addresses.py - Retrieve MSP and Sub's account details (from ARMOR)
2. CONNECTwise_get_accounts_list_and_addresses.py - Retrieve MSP and Sub's account details (from CONNECTwise)
3. ARMOR_match_and_update_CONNECTwise_company_custom_fields.py - Match ARMOR accounts with CONNECTwise accounts, and update custom fields in CONNECTwise.
4. ARMOR_get_tickets_for_account.py - Get support/service tickets from ARMOR
5. CONNECTwise_get_ARMOR_tickets_and_post_to_CONNECTwise_company_service_board.py - Add those tickets to CONNECTwise


## Table of Contents

- [Prequisites](#prerequisites)
- [Security](#security)
- [Sync Companies](#sync-companies)
- [Post Tickets](#post-tickets)

## Prerequisites

CONNECTwise & ARMOR integration workflow:
Prerequisites for the middleware box:
2. Hardened Ubuntu Linux 20.04+
3. Python3
4. ARMOR python scripts

## Security

1. At-Rest: Sensitive credentials
    - All usernames, passwords, account numbers, API keys, public and private keys and clientIds 
      are passed into the Python scripts as command line variables, so that they aren't stored
      anywhere, and also this allows a user to quickly change or modify keys and then turnaround
      and use the same python scripts.
2. In-Transit: 
    - All HTTP calls use HTTPS, so that data on the wire, that is data being transferred to and
      from the ARMOR API and the CONNECTwise API, is always encrypted.

## Sync Companies

1. Sync CONNECTwise companies with ARMOR companies.
    - Create 4 new custom fields for company overview in CONNECTwise.
    - This is done in the CONNECTwise portal under System -> Setup Tables.
      - ARMORcompanyId
      - ARMORcompanyName
      - ARMORparentId
      - ARMORdateUpdated

2. Get ARMOR company accounts and addresses
    - Run python3 script ARMOR_get_accounts_list_and_addresses.py 
    - Input parameters: Armor Username, Armor Password, Armor AccountId 
    - Run example: ./ARMOR_get_accounts_list_and_addresses.py -u testusercompany.com -p Pa$$w0Rd -a XXXX
    - Description: Uses the ARMOR API to pull all master (parent) and sub-accounts (child) for account number XXXX
    - Output: 
      - creates a JSON file named "_response_get_ARMOR_accounts_addresses.json"

3. Get CONNECTwise company accounts and addresses
    - Run python3 script CONNECTwise_get_accounts_list_and_addresses.py 
    - Input parameters: companyId, clientId, publicKey, privateKey
    - Input example: ./CONNECTwise_get_accounts_list_and_addresses.py -coId testcompany_a -clId XXXXXXXX-XXXX-XXXX-XXXXXXXXXXXX -pub publicKey pri privateKey
    - Output:
      - Create a JSON file named "_response_get_CONNECTwise_accounts_and_addresses.json"
    - Output Contents:
      - JSON file contains a list of companyies in CONNECTwise that belong to the clientId, companyId, publicKey and privateKey

4. SYNC Armor companies with CONNECTwise companies
    - Run python3 script ARMOR_match_and_update_CONNECTwise_company_custom_fields.py
    - Description: 
      Match the ARMOR accounts in "_response_get_ARMOR_accounts_addresses.json" with 
      CONNECTwise companies in "_response_get_CONNECTwise_accounts_and_addresses.json"
      and UPDATES those companies in CONNECTwise with ARMOR custom field information. 
    - Input parameters: companyId, clientId, publicKey, privateKey
    - Run example: 
      ./ARMOR_match_and_update_CONNECTwise_company_custom_fields.py -coId testcompany_a -clId XXXXXXXX-XXXX-XXXX-b7fd-XXXXXXXXXXXX -pub publicKey pri privateKey
    - Fields that will be updated in CONNECTwise Company Overview are:
      - ARMORcompanyId - a four digit integer identifying the account id in the Armor Management Portal
      - ARMORcompanyName - a string identifying the account name in the Armor Management Portal
      - ARMORparentId - a four digit integer identifying the account's parent account id in the Armor Management Portal
      - ARMORdateUpdated - a date in ISO-8601 format that this update happened
    - Output:
      - Create a filename for each record updated in CONNECTwise, for example _response_update_CONNECTwise_company_custom_fields_(id)_(name).JSON

## Post Tickets          

1. Tickets from ARMOR to CONNECTwise service tickets.
    - Create a new Service Board named "ARMORtickets" 
    - This is performed in the CONNECTwise portal -> System -> Setup Tables
    - Add Service Ticket statuses of "Completed", "Closed", "New" <- to match statuses that come out of the ARMOR ticketing Portal
    - These statuses are added to the "ARMORtickets" service board, also in System -> Setup Tables

2. Get ARMOR tickets for an Armor AccountId
    - Run Python3 script ARMOR_get_tickets_for_account.py
    - Description: Uses the ARMOR API to pull all tickets (50 at a time) from ARMOR for the specified account XXXX
    - Input parameters: Armor Username, Armor Password, Armor AccountId 
    - Run example: ./ARMOR_get_tickets_for_account.py -u testusercompany.com -p Pa$$w0Rd -a XXXX
    - Output:
      - Creates a JSON file named "_response_get_ARMOR_tickets_for_account_XXXX.json 

3. Get ARMOR tickets and post them to CONNECTwise
    - Run Python3 script CONNECTwise_get_ARMOR_tickets_and_post_to_CONNECTwise_company_service_board.py
    - Description: 
      Uses the ARMOR json response file produced in the previous step as input, Reads the ARMOR account Id from the file,
      finds the matching company in CONNECTwise company, custom field ARMORcompanyId, takes that CONNECTwise company information
      and posts the tickets from the ARMOR file, into the CONNECTwise company's default service board.
    - Input parameters: 
      - CONNECTwise companyId
      - CONNECTwise clientId 
      - CONNECTwise publicKey
      - CONNECTwise privateKey
      - ARMOR Tickets Input File
      - CONNECTwise Service Board (to post the ARMOR tickets to)
    - Run example: ./CONNECTwise_get_ARMOR_tickets_and_post_to_CONNECTwise_company_service_board.py \
      -coId testcompany_a \
      -clId XXXXXXXX-XXXX-XXXX-b7fd-XXXXXXXXXXXX \
     -pub publicKey \
      -pri privateKey \
      -inFile "_response_GET_ARMOR_tickets_for_account_XXXX.json" \
      -SvcBoard "ARMORtickets"
    - Output:
      - Creates a JSON file named "_response_post_CONNECTwise_service_tickets_from_ARMOR_account_XXXX_(CompanyIdentifer).json"
      -> Where XXXX equals the ARMOR AccountId, CompanyIdentifer is the matching Identifier in CONNECTwise

