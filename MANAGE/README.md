
   

This Repo is intended to be used for integration between ARMOR Cloud Security's APIs and
CONNECTwise's APIs - for use by Managed Service Providers (MSPs). This repo applies
specifically to the CONNECTwise "MANAGE" product.

This repository contains:

Files in this repo are all Python3 scripts:
1. ARMOR_get_accounts_list_and_addresses.py - Retrieve MSP and Sub's account details
2. CONNECTwise_get_accounts_list_and_addresses.py - Retrieve MSP and Sub's account details
3. ARMOR_match_and_update_CONNECTwise_company_custom_fields.py - Match ARMOR accounts with CONNECTwise accounts, and update custom fields in CONNECTwise.
4. ARMOR_get_tickets_for_account.py - Get support/service tickets from ARMOR
5. CONNECTwise_get_ARMOR_tickets_and_post_to_CONNECTwise_company_service_board.py - Add those tickets to CONNECTwise


## Table of Contents

- [Prequisites](#prerequisites)
- [Security](#security)

## Prerequisites

CONNECTwise & ARMOR integration workflow:
1. Prerequisites for the middleware box:
2. Hardened Ubuntu Linux 20.04+
3. Python3
4. ARMOR python scripts

## Security

1.a) At-Rest: Sensitive credentials
  All usernames, passwords, account numbers, API keys, public and private keys and clientIds 
  are passed into the Python scripts as command line variables, so that they aren't stored
  anywhere, and also this allows a user to quickly change or modify keys and then turnaround
  and use the same python scripts.

1.b) In-Transit: 
  All HTTP calls use HTTPS, so that data on the wire, that is data being transferred to and
  from the ARMOR API and the CONNECTwise API, is always encrypted.
