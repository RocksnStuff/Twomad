import os
import json
import threading
import random
import time
import requests

from twitterapi import TwitterAPI
from jsondatabase import FileDatabase
from getuser import FetchRetweet

def main():
    bearer_token = open(os.path.dirname(__file__) + '/../bearertoken.txt').read()
    consumer_key = open(os.path.dirname(__file__) + '/../consumerkey.txt').read()
    consumer_secret = open(os.path.dirname(__file__) + '/../consumersecret.txt').read()

    fetch = FetchTweets(60, 3, 240, 743662396892282881, "data", bearer_token, consumer_key, consumer_secret)
    
class FetchTweets(object):
    def __init__(self, polling_interval, tweet_interval, save_interval, user_id, folder, bearer_token, consumer_key, consumer_secret):
        self.rule_tag = "reply"
        self.main_tweets_name = "main_tweets"
        
        self.polling_interval = polling_interval
        self.tweet_interval = tweet_interval
        self.save_interval = save_interval
        self.user_id = user_id
        self.max_rules = 25
        self.folder = folder
        self.fetch = FetchRetweet(consumer_key, consumer_secret)
        
        self.database = FileDatabase(self.folder + "/")
        self.api = TwitterAPI(bearer_token, "https://api.twitter.com/2/")

        self.since_tweet = None
        #self.set_rules_from_memory()

        if self.since_tweet is None:
            self.since_tweet = "1378046099697463297"
        
        self.threads = {
            "pollTimeline": threading.Thread(target=self.poll_timeline_thread, args=("pollTimeline",)),
            "sendTweet": threading.Thread(target=self.send_tweet_thread, args=("sendTweet",)),
            "openStream": threading.Thread(target=self.open_stream_thread, args=("openStream",)),
            "saveData": threading.Thread(target=self.save_data_thread, args=("saveData",))
        }
        #for thread in self.threads.values():
        #    thread.start()

        self.send_tweet_thread("sendTweet")
        
    def set_rules_from_memory(self):
        self.api.clear_stream_rules()
        
        self.tweets_data = self.database.get_file(self.main_tweets_name)
        if self.tweets_data is None or len(self.tweets_data) == 0:
            return None
        for i, tweet in enumerate(self.tweets_data):
            if tweet["tweet"]["conversation_id"] != tweet["tweet"]["id"]:
                self.tweets_data.pop(tweet)
        
        self.since_tweet = self.tweets_data[0]["tweet"]["id"]
        
        conversation_ids = []
        for data in self.tweets_data:
            conversation_ids.append(data["tweet"]["conversation_id"])

        for i, rule_id in enumerate(self.set_rules(*conversation_ids)):
            self.tweets_data[i]["rule_id"] = rule_id
    
    def add_rules(self, *tweets):

        tweets = list(tweets)

        length = len(tweets)
        if length > self.max_rules:
            tweets = tweets[:self.max_rules]

        tweets.reverse()

        rule_delete_ids = []
        conversation_add_ids = []
        for tweet in tweets:
            self.tweets_data.insert(0, {"tweet": tweet})

            if len(self.tweets_data) > self.max_rules:
                rule_delete_ids.append(self.tweets_data.pop(-1)["rule_id"])
            
            conversation_add_ids.append(tweet["conversation_id"])

        self.api.delete_stream_rules(*rule_delete_ids)

        conversation_add_ids.reverse()
        for i, rule_id in enumerate(self.set_rules(*conversation_add_ids)):
            self.tweets_data[i]["rule_id"] = rule_id
        
        self.since_tweet = self.tweets_data[0]["tweet"]["id"]
    
    def set_rules(self, *conversation_ids):
        rules = ["conversation_id:{} has:media is:reply -is:retweet".format(conv_id) for conv_id in conversation_ids]
        return self.api.set_stream_rules(self.rule_tag, *rules)
    
    def poll_timeline_thread(self, name):
        while True:
            response = self.api.get_timeline(self.user_id, "created_at,conversation_id,in_reply_to_user_id,public_metrics", "retweets,replies", self.since_tweet)
            tweets = [tweet for tweet in response if tweet["conversation_id"] == tweet["id"]]
            
            self.add_rules(*tweets)
            self.database.save()

            time.sleep(self.polling_interval)
            
    def send_tweet_thread(self, name):
        self.database.add_file("retweets", [])
        retweets = self.database.get_file("retweets")

        query = "to:{} -is:verified has:media is:reply -is:retweet".format(self.user_id, self.user_id)

        while True:
            tweets = {}
            tweet_likes = []
            next_token = None
            tweet_count = 0
            like_offset = 1
            while True:
                print("Fetching tweets, current tweets:", str(tweet_count))

                try:
                    response = self.api.search_tweets(query, "public_metrics,author_id", next_token)
                except Exception as e:
                    print("An error occurred, retrying.")

                    with open("error_log.txt", 'a') as f:
                        f.write(e)

                for tweet in response["data"]:
                    tweets[tweet["id"]] = tweet
                    tweet_likes.append(tweet["public_metrics"]["like_count"] + like_offset)

                tweet_count += response["meta"]["result_count"]

                if tweet_count >= 500 or "next_token" not in response["meta"]:
                    break

                next_token = response["meta"]["next_token"]

            print(tweets)

            if len(tweets) != 0:
                while True:
                    tweet_id = random.choices(list(tweets.keys()), weights = tweet_likes, k = 1)[0]
                    tweet = tweets[tweet_id]
                    del tweets[tweet_id]
                    if tweet_id in retweets:
                        continue
                    retweets.append(tweet_id)
                    break

                print("printing tweet on thread:", name)
                print(tweet)

                #self.fetch.retweet(tweet_id)
            
            self.database.save()

            time.sleep(self.tweet_interval)
            
    def open_stream_thread(self, name):
        print("stream opened, thread:", name)

        self.database.add_file("replies", [])
        data = self.database.get_file("replies")

        while True:
            response = self.api.get_stream("created_at,conversation_id,public_metrics")

            try:
                for response_line in response.iter_lines():
                    print("response line, thread:", name)

                    if response_line:
                        data.append(json.loads(response_line))
                        print(json.loads(response_line))
            except requests.exceptions.ChunkedEncodingError as e:
                print("incomplete read error in stream; restarting, thread:", name)

                continue

            print("unknown error or response finished; ending thread, thread:", name)
            break

    def save_data_thread(self, name):
        while True:
            print("saving on thread:", name)
            self.database.save()
            
            time.sleep(self.save_interval)

if __name__ == '__main__':
    main()
