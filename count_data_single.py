import json

with open("twomad_tweets_processed.json", "r") as f:
    json_data = json.load(f)
    
print(len(json_data))