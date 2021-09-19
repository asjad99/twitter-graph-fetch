#!/usr/bin/env python
#-----------------------
# Copyright 2014 Halfmoon Labs, Inc.
# All Rights Reserved
#-----------------------

import tweepy
import json
import twitter,time
from pymongo import Connection
from ast import literal_eval
import requests
from html2text import html2text
import urllib2
from urllib2 import HTTPError, urlopen
from urlparse import urlparse
from lxml.html import parse
from lxml.cssselect import CSSSelector

#requirements:
#1. pip install cssselect,html2text,lxml
#2. pip install requests, requests_oauthlib,tweepy,twitter,pymongo

#limit on no. of friends/followers of a single user
#works only when ONLINE_FETCH is True
MAX_CONNECTIONS = 100000

#change to False to remove limit on fetching followers/friends
ONLINE_FETCH = True 

#-------------------------------------------------------

#from twitter_auth import TwitterQueues
#twitter_q = TwitterQueues()

#get an appropriate account from the pool
#users_handle = twitter_q.get_new_handle('users')

#print users_handle

#oauth = users_handle.perform_requests_auth()

#-------------------------------------------------------

def read_link(link, server_root=None):
    try:
      #print ("read_link - link = " + link)
      #raise SystemExit
      url_parsed = urlparse(link)
      url = ""
      if url_parsed.netloc == "":
        url = NetworkIOManager.completeURL(server_root, link)
      else:
        url = link

      print ("------------------------")
      print ("read url = " + url)
      return parse(urlopen(url)).getroot()     
    except (HTTPError, IOError) as e:
      return None

def fetch_url_contents(url):
	try:
		print ("fetching url..." + url)
		r = requests.get(url)
		return r

	except Exception as e:
		print(e)
		return None 


def is_valid_proof(key, value, username):
    proof_url = get_proof_url(value["proof"], username)

    if "username" in value:
        site_username = value["username"]
        if site_username not in proof_url:
        	return False

    r = requests.get(proof_url)
    search_text = html2text(r.text)
    if key == "twitter":
        search_text = search_text.replace("<s>", "").replace("</s>", "").replace("**", "")
    elif key == "github":
        pass
    elif key == "facebook":
        pass
    search_text = search_text.lower()
    if "verifying myself" in search_text and ("+" + username) in search_text:
        return True
    print ('got here')
    return False

def get_proof_url(proof, username):
    proof_url = None
    if "url" in proof:
        proof_url = proof["url"]
    elif "id" in proof:
        if key == "twitter":
            proof_url = "https://twitter.com/" + username + "/status/" + proof["id"]
        elif key == "github":
            proof_url = "https://gist.github.com/" + username + "/" + proof["id"]
        elif key == "facebook":
            proof_url = "https://www.facebook.com/" + username + "/posts/" + proof["id"]
    return proof_url

def verify_profile_social_accounts(onename_id):

	onename_profile_url_json = 'https://onename.io/' + onename_id + '.json'

	result = fetch_url_contents(onename_profile_url_json)

	result = result.json()

	#proof_sites = ["twitter", "github"]
	proof_sites = ["twitter"]

	for key, value in result.items():

		if key in proof_sites and type(value) is dict and "proof" in value:

			if is_valid_proof(key, value, onename_id):
				print key + " account verified"
				return True 
			else:
				print key + " account not verified"
				return False

def monitor_account(onename_id,monitor_time):


	""" moniters a btc address. it will save and return transaction 
	info incase a transaction happens within the next
	15mins of calling """ 

	print 'monitoring account for verification... ' + str(onename_id) 
	
	#time.sleep(60)
	#minutes_passed = 1 
	
	while True:
		if verify_profile_social_accounts(onename_id):
			return True 
				
		time.sleep(60)
		minutes_passed += 1
		print 'minutes passed:' + str(minutes_passed)

		#no verification in monitoring time period. 
		if minutes_passed >= monitor_time:
			print 'exiting...'
			return False  
	
	return None


if __name__ == "__main__":
	print monitor_account('ryanshea',15)










