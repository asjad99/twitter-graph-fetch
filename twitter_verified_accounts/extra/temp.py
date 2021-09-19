def GetFriends(self, user_id=None, screen_name=None, cursor=-1, skip_status=False, include_user_entities=False):
    print "Custom API"
    '''Fetch the sequence of twitter.User instances, one for each friend.

    The twitter.Api instance must be authenticated.

    Args:
        user_id:
            The twitter id of the user whose friends you are fetching.
            If not specified, defaults to the authenticated user. [Optional]
        screen_name:
            The twitter name of the user whose friends you are fetching.
            If not specified, defaults to the authenticated user. [Optional]
        cursor:
            Should be set to -1 for the initial call and then is used to
            control what result page Twitter returns [Optional(ish)]
        skip_status:
            If True the statuses will not be returned in the user items.
            [Optional]
        include_user_entities:
            When True, the user entities will be included.

    Returns:
        A sequence of twitter.User instances, one for each friend
    '''
    if not self.__auth:
        raise TwitterError("twitter.Api instance must be authenticated")
    url = '%s/friends/list.json' % self.base_url
    result = []
    parameters = {}
    if user_id is not None:
        parameters['user_id'] = user_id
    if screen_name is not None:
        parameters['screen_name'] = screen_name
    if skip_status:
        parameters['skip_status'] = True
    if include_user_entities:
        parameters['include_user_entities'] = True

    try: 
        while True:
            parameters['cursor'] = cursor
            json = self._RequestUrl(url, 'GET', data=parameters)
            data = self._ParseAndCheckTwitter(json.content)
            result += [User.NewFromJsonDict(x) for x in data['users']]
            if 'next_cursor' in data:
                if data['next_cursor'] == 0 or data['next_cursor'] == data['previous_cursor']:
                    break
                else:
                    cursor = data['next_cursor']
            else:
                break
        print 'no exception'
        return result, 0
    except Exception, error:
        print "exception"
        #Workaround: Need to fix this!!!
        if str(error) == "[{u'message': u'Rate limit exceeded', u'code': 88}]":
                return result, cursor
        else:
            raise Exception(error)