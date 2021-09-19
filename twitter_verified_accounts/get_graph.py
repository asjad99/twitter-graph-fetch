import tweepy
import tweepy
import json
import twitter
from ast import literal_eval

from twitter_auth import TwitterQueues
twitter_q = TwitterQueues()

#get an appropriate account from the pool
users_handle = twitter_q.get_new_handle('users')


#limit on no. of friends/followers of a single user
#works only when ONLINE_FETCH is True
MAX_CONNECTIONS = 100000

#change to False to remove limit on fetching followers/friends
ONLINE_FETCH = True 


#-------------------------------------------------------
def get_user_details(lookup_list):

    '''
        given a list of Twitter IDs (or screen names) returns the actual Twitter users
    '''

    import requests

    API_URL = 'https://api.twitter.com/1.1/users/lookup.json'
    
    lookup_ids = ""

    for i in lookup_list:
        lookup_ids += str(i) + ', '

    lookup_ids = lookup_ids.rstrip(' ')

    global users_handle
    if users_handle.is_valid(): 
        pass
    else: 
        users_handle = twitter_q.get_new_handle('users')

    print "Using handle: " + users_handle.print_twitter_handle()

    oauth = users_handle.perform_requests_auth()

    r = requests.get(url=API_URL, auth=oauth, params = {'screen_name':lookup_ids})
    r = requests.get(url=API_URL, auth=oauth, params = {'user_id':lookup_ids})

    reply = []

    if(r.status_code == 404):
        pass
    else:
    
        full_result = r.json()

        for i in full_result:

            temp_user = {}
        
            temp_user['twitter_handle'] = i['screen_name'].lower()
            temp_user['full_name'] = i['name'] 
            print temp_user

            reply.append(temp_user)
    
    return reply

#start point 

#1. load the list of verified twitter ids
#-------------------------------------------------------
with open('twitter_verified_ids_list.txt') as f:
    ids_list = [list(literal_eval(line)) for line in f]

ids_list = ids_list[0]

print 'listed loaded with items:'
print len(ids_list)
#-------------------------------------------------------
counter = 0
temp_counter = 100
user_details_list = [] 
user_details = []

while temp_counter < len(ids_list):
    user_details = get_user_details(ids_list[counter:temp_counter])
    user_details_list += user_details
    print 'items fetched' + str(len(user_details))
    temp_counter += 100
    counter +=100

with open('twitter_verified_accountdetails_list.txt', 'w') as outfile:
    json.dump(user_details_list,outfile) 




