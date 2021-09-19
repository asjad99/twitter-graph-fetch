#!/usr/bin/env python
#-----------------------
# Copyright 2013 Halfmoon Labs, Inc.
# All Rights Reserved
#-----------------------

'''
    for performing/saving Twitter auth (both Tweepy and generic OAuth over HTTP)
    and for maintaining TwitterQueues (pools) of users for specific API end-points 
'''

#from common import *
#from graph.twitter.config import *

import tweepy

import Queue 
from pymongo import MongoClient

c = MongoClient()
twitter_auth = c['twitter_auth']

#limit on no. of friends/followers of a single user

#no. of retries before giving up
MAX_RETRY = 10

#how many users to use in user_pool 
MAX_USERS_IN_POOL = 100 

#---------------------------------------
def get_app_token(app_name):

    reply = twitter_auth.apps.find_one({'app_name':app_name})

    consumer_key = str(reply['consumer_key'])
    consumer_secret = str(reply['consumer_secret'])

    return consumer_key,consumer_secret

#globals
CONSUMER_KEY, CONSUMER_SECRET = get_app_token('onename_stats')

import threading

#-------------------------
class RateLimitThread(threading.Thread):
    def __init__(self,user):
        threading.Thread.__init__(self)
        self.user=user
        api = perform_tweepy_auth(user['access_key'],user['access_secret'])
        #api = perform_tweepy_auth('133430191-o5ouFcL7AZupJo9pAuyPC9gW20gejSkentmsZEBd', 'YNHEgwKH6fZFO9PUpn2TqeXf0yNxy1vPpGmpSJfsWO8fw')
        self.reply = check_rate_limit(api,'users')
        #self.reply = check_rate_limit(api,'users')


#---------------------------------------
class TwitterQueues(object):
    '''
        this class holds queues for variosu Twitter API end-points
        the users in each queue can access the respectice end-points 
        this is meant for aggregating the API_LIMIT available 
    '''
    def __init__(self, q_size=MAX_USERS_IN_POOL):
        self.q_size = q_size

        #Queues for different types of API calls
        self.friends_q = Queue.Queue()
        self.followers_q = Queue.Queue()
        self.users_q = Queue.Queue()
        self.timeline_q = Queue.Queue()

        self.refresh() 

    #---------------------------------------
    def refresh(self):

        counter = 0
        users = []


        #TODO: make this random instead of a serial loop (i.e., pick users at random from pool)
        for user in twitter_auth.users.find():
            users.append(user)
            #no need to get all accounts, a subset is fine
            if(counter == self.q_size):
                break 

        threads = [] 

        for i in users:
            threads.append(RateLimitThread(i)) 

        #start all threads
        [x.start() for x in threads]

        #wait for all of them to finish
        [x.join() for x in threads] 
     
        #for now selecting users with at least 50% of their API limit left
        for thread in threads: 

            reply = thread.reply
            user = thread.user

            for i in reply:

                if( (i['resource'] == 'friends') and (i['status']['limit'] > 2) ):
                    self.friends_q.put(user)

                if( (i['resource'] == 'followers') and (i['status']['limit'] > 2) ):
                    self.followers_q.put(user)

                if( (i['resource'] == 'users') and (i['status']['limit'] > 2) ):
                    self.users_q.put(user)

    #---------------------------------------
    def print_q_status(self):

        #not the best way to print, but works for now (should not pop and then call refresh) 

        #-------------------------------
        print '-' * 5
        print "Friends Q: "

        while not self.friends_q.empty():
            user = self.friends_q.get()
            print user['twitter_handle']

        #-------------------------------
        print '-' * 5
        print "Followers Q: "

        while not self.followers_q.empty():
            user = self.followers_q.get()
            print user['twitter_handle']

        #-------------------------------
        print '-' * 5
        print "Users Q: "

        while not self.users_q.empty():
            user = self.users_q.get()
            print user['twitter_handle']

        self.refresh()

    #---------------------------------------
    def get_new_friends_handle(self):
        '''
            return a user from the queue that can access the /friends/ids end-point
        '''

        if not self.friends_q.empty():
            user = self.friends_q.get()
            print user  
            return TwitterHandle(user, 'friends')
        else:
            print("got here")
            self.refresh() 
            return None 

    #---------------------------------------
    def get_new_followers_handle(self):
        '''
            return a user from the queue that can access the /followers/ids end-point
        '''
    
        if not self.followers_q.empty():
            user = self.followers_q.get()
            return TwitterHandle(user, 'followers')
        else:
            self.refresh() 
            return None 

    #---------------------------------------
    def get_new_users_handle(self):
        '''
            return a user from the queue that can access the /users/lookup end-point
        '''   
        if not self.users_q.empty():
            user = self.users_q.get()
            return TwitterHandle(user, 'users') 
        else:
            self.refresh() 
            return None
    #----------------------------
    def get_new_handle(self, graph_type):

        while(1):
            if(graph_type == 'followers'):
                handle = self.get_new_followers_handle()
            elif(graph_type == 'friends'):
                handle = self.get_new_friends_handle()
            elif(graph_type == 'users'): 
                handle = self.get_new_users_handle()

            if handle is not None and handle.is_valid():
                return handle
            
            if handle is None:
                print "Hitting API limit. Sleeping ... "
                self.refresh()
                import time
                time.sleep(60)
    

#---------------------------------------
class TwitterHandle(object):
    '''
        for getting a handle/user for a particular end-point resource 
    '''

    def __init__(self, user, resource='none'):
        self.user = user
        self.resource = resource
        #assuming that tweepy api gets used more often, so save it
        self.api = perform_tweepy_auth(self.user['access_key'],self.user['access_secret'])
        self.oauth = None 
    #---------------------------------------
    def print_twitter_handle(self):
        while 1:
            try:
                return self.api.me().screen_name
            except:
                print 'api limit reached...sleeping'
                self.refresh()
                import time
                time.sleep(60)

    #---------------------------------------
    def get_limit(self):
        return check_rate_limit(self.api, self.resource)

    #---------------------------------------

    def is_valid(self):
        reply = check_rate_limit(self.api, check_resources = self.resource)
        
        for i in reply:

            if(i['resource'] == self.resource):

                print str(i['status']['remaining'])

                #leave last two calls as buffer
                if(i['status']['remaining'] > 2):
                    return True 
                else:
                    return False
        return False

    #---------------------------------------
    #assuming that requests oauth doesn't get used that often 
    def perform_requests_auth(self):
        #after first call self.oauth will work
        self.oauth = perform_requests_auth(key=self.user['access_key'],secret=self.user['access_secret']) 
        return self.oauth 

#---------------------------------------
def check_rate_limit(api, check_resources='none'):

    '''
        if no resources are specified, then check all resources 
        input should be comma separated resources to check 
    '''

    #-----------------------------
    #internal function
    def check_limit_with_retry(retry_limit=MAX_RETRY):

        counter = 0

        while(1):
        
            counter += 1

            #if(counter == retry_limit):
            #    return False

            try:
                if(check_resources is 'none'):
                    status = api.rate_limit_status() 
                    
                    return status

                else:
                    #stongly encouraged to specify which resource you want to check limits for
                    status = api.rate_limit_status(resources=check_resources)
                    #print api.me().screen_name  
                    return status

            except Exception as e:
                print "Sleeping on error" 
                import time
                time.sleep(60)
    #-----------------------------

    status = check_limit_with_retry()

    if(status == False):
        print "ERROR: Twitter seems to be down ... "
        return status 

    if(check_resources is 'none'):
        #return the full reply if no resource given
        return status 

    #reach here only if 1 or more resources were specified 
    resources = check_resources.rsplit(',')

    #-----------------------------
    #internal function
    def convert_to_min(input):

        from datetime import datetime
        reset_time = datetime.fromtimestamp(input['reset'])
    
        time_now = datetime.now()
        time_remaining = reset_time - time_now

        remaining_mins = round(time_remaining.total_seconds() / 60,2) 

        #change reset time to minutes instead of UNIX epoc 
        input['reset'] = remaining_mins

        return input
    #-----------------------------

    reply = []

    for i in resources:

        #add the resources you're interested in here, and they'll get appended
        if(i == 'friends'):
            temp = {}
            temp['resource'] = i 
            temp['status'] = convert_to_min(status['resources']['friends']['/friends/ids'])
            reply.append(temp)
        elif(i == 'followers'):
            temp = {}
            temp['resource'] = i 
            temp['status'] = convert_to_min(status['resources']['followers']['/followers/ids'])
            reply.append(temp)
        elif(i == 'users'):
            temp = {}
            temp['resource'] = i 
            temp['status'] = convert_to_min(status['resources']['users']['/users/show/:id'])
            reply.append(temp)  

    return reply

#---------------------------------------
def save_app_auth(name,key,secret):

    '''
        for saving app consumer_key/secret (won't be used often) 
    '''

    app = {}
    app['app_name'] = name
    app['consumer_key'] = key
    app['consumer_secret'] = secret

    twitter_auth.apps.save(app) 

#---------------------------------------
def save_user_auth(handle,key,secret):

    '''
        for saving user access_key/secret 
    '''

    reply = twitter_auth.users.find_one({'twitter_handle':handle})

    #update the token if the user already in DB
    if reply is not None:
        user = reply
    else:
        user = {}
        user['twitter_handle'] = handle    
    
    user['access_key'] = key
    user['access_secret'] = secret

    twitter_auth.users.save(user)

    print 'saved'

#---------------------------------------
def perform_tweepy_auth(key, secret):

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

    auth.set_access_token(key,secret)

    try:
        api = tweepy.API(auth)

    except Exception as e:
        print 'exception'
        print e

    return api

#---------------------------------------
def perform_requests_auth(key, secret):

    from requests_oauthlib import OAuth1

    oauth = OAuth1(CONSUMER_KEY,
                client_secret=CONSUMER_SECRET,
                resource_owner_key=key,
                resource_owner_secret=secret)

    return oauth

#---------------------------------------
def get_new_auth():

    '''
        this function is for getting auth of a new user (from command line)
    '''

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth_url = auth.get_authorization_url()
    print 'Please authorize: ' + auth_url
    verifier = raw_input('PIN: ').strip()
    auth.get_access_token(verifier)
    print "ACCESS_KEY = '%s'" % auth.access_token.key
    print "ACCESS_SECRET = '%s'" % auth.access_token.secret

    key = auth.access_token.key
    secret = auth.access_token.secret 

    api = tweepy.API(auth)

    handle = api.me().screen_name

    print handle
    #saving to our MongoDB
    save_user_auth(handle,key,secret)
    print 'saved'

#---------------------------------------
def debug():
    
    reply = twitter_auth.users.find_one({'twitter_handle':'ibrahimahmed443'})

    api = perform_tweepy_auth(reply['access_key'],reply['access_secret']) 
    
    api.me().screen_name

    print (check_rate_limit(api,'friends,followers,users'))



    users = TwitterQueues() 
    users.print_q_status() 
    
    return

#---------------------------------------
if __name__ == "__main__":
  
    debug()
    #run save_app_auth
    #then change app_name accordingly in get_app_token
    #lastly run get_new_auth()

    #save_app_auth('onename_stats','HzlxMlfbLyPnMFslJ3aW51XpQ','ZhuAkiAs19c1tPqmfg1jq9wzd2NKaIw61qaIb9EhzzsrzQkK5e')
    #get_new_auth()
