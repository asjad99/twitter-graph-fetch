
#!/usr/bin/env python
#-----------------------
# Copyright 2014 Halfmoon Labs, Inc.
# All Rights Reserved
#-----------------------

import json
import pymongo
from pymongo import Connection
from ast import literal_eval


con = Connection()
db = con['angellist']

users = db.users

#returns a twitter handle, given a twitter_url
def gethandle(twitter_url):

	handle = ""
	index = 0

	print 'twitter_url' + twitter_url 
	
	index = twitter_url.find('.com/',index)

	handle = twitter_url[index + 5:]
	
	#recheck for any additional symbols after primary url 'http://twitter.com/'' string. 
	index = 0
	index = handle.find('/',index)

	while True:
			
			if handle.find('/',index) == -1:
				break
			else:
				handle = handle[index + 1:]
				print handle
				if handle.find('&',index) != -1:
					break
				index = handle.find('/',0)

	print 'final handle:'+ handle
	
	return handle

angellist_twitter_handles_list = []
#---------------------------------------------
#1. fetch twitter handles from angellist data
#---------------------------------------------
for user in users.find():
	twitter_url = user['twitter_url']

	#parse the url to get the handle 
	if twitter_url != None:
		handle = gethandle(twitter_url)
		
	if handle != None and handle != "":
		angellist_twitter_handles_list.append(handle)

print 'items_saved' + str(len(angellist_twitter_handles_list))

#1.1 remove dublicates
#---------------------------------------------
angellist_twitter_handles_list = list(set(angellist_twitter_handles_list))


#1.2 save the list of twitter handles(if needed)
#---------------------------------------------
with open('angel_list_twitter_handles.txt', 'w') as outfile:
    json.dump(angellist_twitter_handles_list,outfile) 

twitter_verified_handle_list = []
#-------------------------------------------------------
#2. load the verified twitter accounts list
#-------------------------------------------------------
with open('twitter_verified_accountdetails_list.txt') as f:
    twitter_list = [list(literal_eval(line)) for line in f]

twitter_list = twitter_list[0]
print 'listed loaded with items:'
print len(twitter_list)

#separete twitter_handles list
for user_dict in twitter_list:
	twitter_verified_handle_list.append(user_dict['twitter_handle'])

#print len(twitter_verified_handle_list)

#-------------------------------------------------------
#3. find and save the common users in angellist data and twitter verified accounts
#-------------------------------------------------------
final_user_list= []

#final_user_list = list(set(twitter_verified_handle_list).intersection(angellist_twitter_handles_list))

"""  
alog. for comparing lists 
(note: it has a quadratic complexity, should not be used for large datasets)

for item in range(len(angellist_twitter_handles_list)):
	user = angellist_twitter_handles_list[item]
	if user in twitter_verified_handle_list:
		final_user_list.append(user)


"""
#saving the list...
with open('angel_list_and_verified_accounts_interesection.txt', 'w') as outfile:
    json.dump(final_user_list,outfile) 


print 'total common users' + str(len(final_user_list))
print 'done'

