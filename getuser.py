import tweepy
import os

# In your terminal please set your environment variables by running the following lines of code.
# export 'CONSUMER_KEY'='<your_consumer_key>'
# export 'CONSUMER_SECRET'='<your_consumer_secret>'

class FetchRetweet(object):
    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        
        self.auth()
        self.start_api()
        
    def auth(self):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)

        # Open authorization URL in browser
        print(auth.get_authorization_url())
    
        # Ask user for verifier pin
        pin = input('Verification pin number from twitter.com: ')
        
        # Get access token
        token = auth.get_access_token(pin)
        auth.set_access_token(token[0], token[1])
        
        self.auth = auth
        
    def start_api(self):
        self.api = tweepy.API(self.auth)
        
    def retweet(self, tweet_id):        
        self.api.retweet(tweet_id)