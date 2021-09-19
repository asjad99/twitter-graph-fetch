
DEBUG = False

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5000

#------------- globals --------
#Twitter API limits to 200 tweets per call
TWEETS_PERCALL = 200

#no. of retries before giving up
MAX_RETRY = 10

#pause/sleep when hitting rate limits, in seconds
SLEEP_ON_RATE_LIMIT = 60

#pause/sleep when some error, in seconds
SLEEP_ON_ERROR = 5

#current values of different Twitter API end-point limits
#defined by Twitter, not us
TWITTER_LIMIT_FRIENDS_IDS = 15
TWITTER_LIMIT_FOLLOWERS_IDS = 15
TWITTER_LIMIT_USERS_LOOKUP = 180

#how many users to use in user_pool 
MAX_USERS_IN_POOL = 100 

#limit on no. of friends/followers of a single user
#works only when ONLINE_FETCH is True
MAX_CONNECTIONS = 100000

#change to False to remove limit on fetching followers/friends
ONLINE_FETCH = True 

#when fetched results go stale, in days
FETCHED_RESULTS_EXPIRY = 30

#XX move these somewhere else 
APP_USERNAME = 'scopeapp'
APP_PASSWORD = 'password'