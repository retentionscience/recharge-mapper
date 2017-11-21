#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Dependencies
import sys
import paramiko
import json
import csv
import requests 
import hashlib
import time
from datetime import datetime
from datetime import timedelta
from ratelimit import rate_limited

RUN_HISTORICAL = False

# ReSci SFTP Credentials
API_USER = "your-api-key"
API_PASS = "your-api-pass"
API_URL = "sftp1.retentionscience.com"
PORT = 22

# ReCharge API Token
RECHARGE_KEY  = "Recharge-api-key"
RECHARGE_URL  = "https://api.rechargeapps.com/"

HEADERS = {"X-Recharge-Access-Token": RECHARGE_KEY }

# Helper Functions

# Call ReCharge API
def call_recharge_api(url):
	page = ''
	while page == '':
		try:
			page = requests.get(url, headers = HEADERS )
		except:
			print 'Connection refused by the server..'
			print 'Retrying in 5 seconds'
			time.sleep(5)
			print 'Attempting to reconnect to server'
			continue
	return page

# Md5 Hash Email
def md5_record_id(email):
	md5hash_record_id = hashlib.md5()
	md5hash_record_id.update(email.lower())
	return md5hash_record_id.hexdigest()

# Get Shopify Customer Id
@rate_limited(1,2)
def get_shopify_customer_id(customer_id):
	result = call_recharge_api(RECHARGE_URL + "customers/%s" %(customer_id))
	customer = json.loads(result.text)
	user_record_id = customer['customer']['shopify_customer_id']
	return user_record_id if user_record_id else md5_record_id(customer['customer']['email'])

# Get Subscription Data
@rate_limited(1)
def get_subscriptions(start_date, end_date, page):
	result = call_recharge_api(RECHARGE_URL + "subscriptions?updated_at_min=%s&updated_at_max=%s&page=%s" %(str(start_date.strftime("%Y-%m-%dT%H:%M:%S")), str(end_date.strftime("%Y-%m-%dT%H:%M:%S")), page))
	subscriptions = json.loads(result.text)
	return subscriptions['subscriptions']

def is_churned(status):
	return int(status == 'CANCELLED')

# Trials are managed differently per business. Please adjust logic accordingly
def is_trial(subscription):
	if subscription['next_charge_scheduled_at'] == None:
		return 0

	# Note: ReCharge suggest using charge_delay to track trial subscriptions
	#	Feel free to modify this for your own business case.
	charge_delay = None
	properties = subscription['properties']
	if properties == None:
		return 0
	else:
		for property in properties:
			if property['name'] == 'charge_delay':
				charge_delay = property['value']
				break

		if charge_delay == None:
			return 0
		else:
			created_at = datetime.strptime(subscription['created_at'], '%Y-%m-%dT%H:%M:%S').date()
			next_charge_scheduled_at = datetime.strptime(subscription['next_charge_scheduled_at'], '%Y-%m-%dT%H:%M:%S').date()
			first_nontrial_charge_date = created_at + timedelta(days=int(charge_delay))
			return int(next_charge_scheduled_at <= first_nontrial_charge_date) 

def datetime_to_string(dt):
	if dt is None:
		return None
	for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S'):
		try:
			return str(datetime.strptime(dt, fmt))
		except ValueError:
			pass
	raise ValueError('no valid date format found')

def create_header():
	return ['record_id', 'user_record_id', 'status', 'item_record_id', 'started_at', 'trial', 'churned', 'canceled_at']

def create_subscription_row(subscription):
	return {
		'record_id': subscription['id'],
		'user_record_id': get_shopify_customer_id(subscription['customer_id']),
		'status': str(subscription['status']),
		'item_record_id': subscription['shopify_variant_id'],
		'started_at': datetime_to_string(subscription['created_at']),
		'trial': is_trial(subscription),
		'churned': is_churned(subscription['status']),
		'canceled_at': datetime_to_string(subscription['cancelled_at'])
	}

def create_tsv(file_name):
	today = datetime.utcnow()
	two_days_ago = today - timedelta(days=2) if RUN_HISTORICAL is False else datetime(1950, 1, 1, 0, 0, 0)
	page = 1

	with open(file_name, 'wb') as csvfile:
		writer = csv.DictWriter(csvfile, create_header(), delimiter='\t')

		writer.writeheader()

		# Retrieves Subscriptions updated in the past 48 hour and maps them into a .tsv
		subscriptions = get_subscriptions(two_days_ago, today,page)

		while len(subscriptions) != 0:
			for subscription in subscriptions:
				print '.',
                		subscription_row = create_subscription_row(subscription)
                		writer.writerow(subscription_row)
			page += 1
			subscriptions = get_subscriptions(two_days_ago, today,page)


def main():
	diff_file_name = 'subscriptions_%s.tsv' %(str(datetime.utcnow().strftime("%Y-%m-%d_%H:%M"))) if RUN_HISTORICAL is False else 'subscriptions_hist.tsv'

	print 'Generating user_subscription file'
    	create_tsv(diff_file_name)
    	print 'Generated user_subscription file'

	try:
		# Open SFTP

		# Open a transport
		transport = paramiko.Transport((API_URL, PORT))

		# Auth
		transport.connect(username = API_USER, password = API_PASS)

		# Go!
		sftp = paramiko.SFTPClient.from_transport(transport)

		print 'Uploading subscription file to SFTP'
        	sftp.put(diff_file_name, diff_file_name)
        	print 'Uploaded subscription file to SFTP'

	finally:
		# Close
		sftp.close()
		transport.close()
		print 'ReCharge Mapper Executed'

# Script Starts Here

if __name__ == "__main__": main()
