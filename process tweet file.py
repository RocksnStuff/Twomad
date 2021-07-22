import json

with open("twomad_tweets.json", "r") as f:
    json_data = json.load(f)

pages = [page["data"] for page in json_data if "data" in page]

tweets = []
for page in pages:
    for tweet in page:
        if "in_reply_to_user_id" not in tweet or ("in_reply_to_user_id" in tweet and tweet["in_reply_to_user_id"] == "743662396892282881"):
            tweets.append(tweet)
            
with open("twomad_tweets_processed.json", "w") as f:
    json.dump(tweets, f, indent=4, sort_keys=True)