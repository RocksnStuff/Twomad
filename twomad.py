import requests
import os
import json

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'


def auth():
    return os.environ.get("BEARER_TOKEN")


def create_url():
    # Replace with user ID below
    user_id = 743662396892282881
    return "https://api.twitter.com/2/users/{}/tweets".format(user_id)


def get_params(pagination_token):
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    params = {"tweet.fields": "created_at,conversation_id,in_reply_to_user_id,public_metrics", "exclude": "replies", "max_results": 100}
    
    if pagination_token == None:
        return params
    
    params["pagination_token"] = pagination_token
    return params


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers, params):
    response = requests.request("GET", url, headers=headers, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def print_pagination(url, headers, params):
    json_data = print_pagination_recurse([], url, headers, params, 1)
    
    f = open("twomad_tweets_no_replies_retweets.json", "w")
    f.write(json.dumps(json_data, indent=4, sort_keys=True))
    f.close()
    
    print("Successfully requested tweets.")


def print_pagination_recurse(json_data, url, headers, params, counter):
    json_response = connect_to_endpoint(url, headers, params)
    json_data.append(json_response)
    
    print("Requested", counter, "page(s).")
    
    if "next_token" not in json_response["meta"]:
        return json_data
    
    return print_pagination_recurse(json_data, url, headers, get_params(json_response["meta"]["next_token"]), counter + 1)


def main():
    bearer_token = auth()
    url = create_url()
    headers = create_headers(bearer_token)
    params = get_params(None)
    
    print_pagination(url, headers, params)

if __name__ == "__main__":
    main()