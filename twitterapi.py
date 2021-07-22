import requests

class TwitterAPI(object):
    
    def __init__(self, bearer_token, suffix):
        self._bearer_token = bearer_token
        self._prefix = suffix
        self._headers = self.__create_headers()
       
    
    #setup----------------------------------------------------------------------------------
    def __create_headers(self):
        headers = {"Authorization": "Bearer {}".format(self._bearer_token)}
        return headers
    
    def __connect_to_endpoint(self, suffix, method="GET", success=200, params=None, error_message="Request returned an error", return_json=True, **arg):
        url = self._prefix + suffix

        response = requests.request(method, url, headers=self._headers, params=params, **arg)
        
        if response.status_code != success:
            raise Exception(
                "{}: {} {}".format(
                    error_message, response.status_code, response.text
                )
            )
            
        if return_json:
            return response.json()
        return response

    #timeline endpoint----------------------------------------------------------------------------------
    def __get_timeline_params(self, since_tweet, tweet_fields, exclude):
        # Tweet fields are adjustable.
        # Options include:
        # attachments, author_id, context_annotations,
        # conversation_id, created_at, entities, geo, id,
        # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
        # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
        # source, text, and withheld
        params = {"tweet.fields": tweet_fields, "exclude": exclude, "max_results": 100}
        if since_tweet != None:
            params["since_id"] = since_tweet

        return params
    
    def __get_timeline_recurse(self, url, params, json_data):
        json_response = self.__connect_to_endpoint(url, params=params)

        if "data" in json_response:
            json_data.extend(json_response["data"])

        if "next_token" not in json_response["meta"]:
            return json_data
        
        params["pagination_token"] = json_response["meta"]["next_token"]
        return self.__get_timeline_recurse(url, params, json_data)
    
    def get_timeline(self, user, tweet_fields, exclude, since_tweet = None):
        suffix = "users/{}/tweets".format(user)
        params = self.__get_timeline_params(since_tweet, tweet_fields, exclude)
        
        return self.__get_timeline_recurse(suffix, params, [])
    
    
    #filtered stream endpoint----------------------------------------------------------------------------------
    def get_stream_rules(self):
        return self.__connect_to_endpoint("tweets/search/stream/rules", error_message="Cannot get rules")
    
    def set_stream_rules(self, tag, *values):
        if len(values) == 0:
            return []

        suffix = "tweets/search/stream/rules"
        rules = [{"value": value, "tag": tag} for value in values]
        payload = {"add": rules}
        
        json_response = self.__connect_to_endpoint(suffix, method="POST", success=201, error_message="Cannot add rules", json=payload)

        if "data" in json_response:
            return [data["id"] for data in json_response["data"]]
        return []
    
    def delete_stream_rules(self, *ids):
        if len(ids) == 0:
            return

        suffix = "tweets/search/stream/rules"
        payload = {"delete": {"ids": ids}}
        
        self.__connect_to_endpoint(suffix, method="POST", error_message="Cannot delete rules", json=payload)
        
    def clear_stream_rules(self):
        rules = self.get_stream_rules()
        
        if "data" not in rules:
            return None
        
        ids = [rule["id"] for rule in rules["data"]]
        
        self.delete_stream_rules(*ids)
    
    def get_stream(self, tweet_fields):
        params = {"tweet.fields": tweet_fields}
        return self.__connect_to_endpoint("tweets/search/stream", params=params, error_message="Cannot get stream", return_json=False, stream=True)