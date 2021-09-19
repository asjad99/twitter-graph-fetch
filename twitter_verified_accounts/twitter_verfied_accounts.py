
#!/usr/bin/env python
#-----------------------
# Copyright 2014 Halfmoon Labs, Inc.
# All Rights Reserved
#-----------------------

import tweepy
import time
import tweepy
import json
import twitter
from ast import literal_eval

# == OAuth Authentication ==
#
# This mode of authentication is the new preferred way
# of authenticating with Twitter.

# The consumer keys can be found on your application's Details
# page located at https://dev.twitter.com/apps (under "OAuth settings")
consumer_key="HzlxMlfbLyPnMFslJ3aW51XpQ"
consumer_secret="ZhuAkiAs19c1tPqmfg1jq9wzd2NKaIw61qaIb9EhzzsrzQkK5e"

# The access tokens can be found on your applications's Details
# page located at https://dev.twitter.com/apps (located 
# under "Your access token")
access_token="133430191-o5ouFcL7AZupJo9pAuyPC9gW20gejSkentmsZEBd"
access_token_secret="YNHEgwKH6fZFO9PUpn2TqeXf0yNxy1vPpGmpSJfsWO8fw"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

#api = tweepy.API(auth)

api = twitter.Api(consumer_key='HzlxMlfbLyPnMFslJ3aW51XpQ',
                      consumer_secret='ZhuAkiAs19c1tPqmfg1jq9wzd2NKaIw61qaIb9EhzzsrzQkK5e',
                      access_token_key='133430191-o5ouFcL7AZupJo9pAuyPC9gW20gejSkentmsZEBd',
                      access_token_secret='YNHEgwKH6fZFO9PUpn2TqeXf0yNxy1vPpGmpSJfsWO8fw')

# If the authentication was successful, you should
# see the name of the account print out

#print api.me().name


# If the application settings are set for "Read and Write" then
# this line should tweet out the message to your account's 
# timeline. The "Read and Write" setting is on https://dev.twitter.com/apps
#api.update_status('Updating using OAuth authentication via Tweepy!')

"""
#-------------------------------------
#fetching 94k followers list of twitter verified accounts ids 
#-------------------------------------


ids_list = []

for page in tweepy.Cursor(api.friends_ids, screen_name="verified").pages():
	ids_list.extend(page)
	print "number of ids fetched = " + str(len(ids_list))
	time.sleep(60)

print "total account ids feteched:"
print len(ids_list)

with open('twitter_verified_ids_list.txt', 'w') as outfile:
	json.dump(ids_list,outfile) 

"""
"""

#-------------------------------------
#load the list of verified twitter ids
#-------------------------------------


with open('twitter_verified_ids_list.txt') as f:
    ids_list = [list(literal_eval(line)) for line in f]

ids_list = ids_list[0]

#fetch the account details 

user_details_list = []

for id in ids_list: 
	user = api.GetUser(id)

	print user.name 
	user_details_list.append((user.name,user.screen_name))
	#print user_details_list

#users = api.GetFriends('muneeb')

with open('twitter_verified_accountdetails_list.txt', 'w') as outfile:
	json.dump(user_details_list,outfile) 

"""


"""
##-------------------------------------
#using twitter python to fetch friends
#-------------------------------------


user_details_list = []

friends_list =  api.GetFriends(screen_name='verified')

for user in friends_list:
	print user.name
	user_details_list.append((user.name,user.screen_name))

print "total friends fetched:"
print len(user_details_list)

with open('twitter_verified_accountdetails_list.txt', 'w') as outfile:
	json.dump(user_details_list,outfile) 

"""

#-------------------------------------
#create a csv file
#-------------------------------------

"""
import csv

ofile  = open('ttest.csv', "wb")
writer = csv.writer(ofile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)

for item in user_details_list:
    writer.writerow(item)

ofile.close()
"""





