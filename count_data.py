import json

with open("twomad_tweets_no_replies.json", "r") as f:
    json_data = json.load(f)

pages = [page["data"] for page in json_data if "data" in page]

counter = 0
tweets = []
for page in pages:
    for tweet in page:
        tweets.append(tweet)
        if "in_reply_to_user_id" in tweet and tweet["in_reply_to_user_id"] != "743662396892282881":
            counter += 1

print(counter)
print(len(tweets))