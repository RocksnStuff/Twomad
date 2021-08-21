import os

from twitterapi import TwitterAPI

def main():
    bearer_token = open(os.path.dirname(__file__) + '/../bearertoken.txt').read()

    api = TwitterAPI(bearer_token, "https://api.twitter.com/2/")

    print(api.get_tweet(1421892854943821832, "referenced_tweets"))

if __name__ == '__main__':
    main()