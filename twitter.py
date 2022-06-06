import requests
import json
import tweepy
import sys
from pprint import pprint

class Twitter:
    def __init__(self, auth_location="./auth.json"):
        try:
            with open(auth_location, "r") as auth_file:
                data = json.load(auth_file)
                self.bearer_token=data["bearer_token"]
                self.access_token=data["access_token"]
                self.access_token_secret=data["access_token_secret"]
                self.consumer_key=data["consumer_key"]
                self.consumer_secret=data["consumer_secret"]

        except FileExistsError or FileNotFoundError or KeyError as err:
            sys.exit(f"Error: {err}. Failed to init - please check README.md")

    def get_client(self):
        return tweepy.Client(bearer_token=self.bearer_token)

def main():
    twitter=Twitter()
    user_id="216776631"
    client = twitter.get_client()
    tweets = client.get_users_tweets(user_id)
    pprint(tweets)

main()
# #its bad practice to place your bearer token directly into the script (this is just done for illustration purposes)
# BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAHLbcQEAAAAACQDD3jWZnDzSx%2BdApUVxGmupoUU%3D0p49WEOkZowtirzHP0Do652zRJ9JpSYFqqNKqozDsOKCUV3L2C"
# #define search twitter function
# def search_twitter(query, tweet_fields, bearer_token = BEARER_TOKEN):
#     headers = {"Authorization": "Bearer {}".format(bearer_token)}

#     url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}".format(
#         query, tweet_fields
#     )
#     response = requests.request("GET", url, headers=headers)

#     print(response.status_code)

#     if response.status_code != 200:
#         raise Exception(response.status_code, response.text)
#     return response.json()

# #search term
# query = "(from:BernieSanders)"
# #twitter fields to be returned by api call
# tweet_fields = "tweet.fields=text,author_id,created_at"

# #twitter api call
# json_response = search_twitter(query=query, tweet_fields=tweet_fields, bearer_token=BEARER_TOKEN)
# #pretty printing
# print(json.dumps(json_response, indent=4, sort_keys=True))