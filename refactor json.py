import json

with open("data/twomad_tweets_processed.json", "r") as f:
    raw_data = json.load(f)

data = [{"tweet": line} for line in raw_data]
with open("data/main_tweets.json", "w") as f:
    json.dump(data, f, indent=4, sort_keys=True)