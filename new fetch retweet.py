import tweepy
import os

"""
    Query the user for their consumer key/secret
    then attempt to fetch a valid access token.
"""

if __name__ == "__main__":

    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

    # Open authorization URL in browser
    print(auth.get_authorization_url())

    # Ask user for verifier pin
    pin = input('Verification pin number from twitter.com: ')
    
    # Get access token
    try:
        token = auth.get_access_token(pin)
    except tweepy.TweepError:
        print('Error! Failed to get access token.')

    # Give user the access token
    print ('Access token:', token)