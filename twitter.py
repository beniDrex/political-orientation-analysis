import requests
import json
import tweepy
import sys
from pprint import pprint
from bs4 import BeautifulSoup
import csv 

class User:
    def __init__(self, username, id, name, political_party):
        self.username=username
        self.id=id
        self.name=name
        self.political_party=political_party
        self.tweets=[]
        self.engaged_users=[]
        self.shared_urls=[]
    
    def __str__(self):
        return f"Username: {self.username}, Name: {self.name}, Political Party: {self.political_party}"

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

        self.client=tweepy.Client(bearer_token=self.bearer_token, wait_on_rate_limit=True)

    def get_client(self):
        self.client=tweepy.Client(bearer_token=self.bearer_token)

    def get_users(self, political_party, usernames=[]):
        length = len(usernames)
        users=[]
        if self.client is None:
            self.get_client()\
        # max ids per request = 100 
        step=99
        for i in range(99, length, step):
            resp = self.client.get_users(usernames=usernames[i-step:i], user_fields=["username", "name", "id"])
            for user in resp.data:
                u = User(user.username, user.id, user.name, political_party)
                users.append(u)
            # Use the remaining users < 100
            if i+step>=length:
                resp = self.client.get_users(usernames=usernames[i:length], user_fields=["username", "name", "id"])
                for user in resp.data:
                    u = User(user.username, user.id, user.name, political_party)
                    users.append(u)

        return users


def starting_twitter_handles(file="./representative-twitters.csv"):
    with open(file, "r") as data:
        democrats=[]
        republicans=[]
        csv_data=csv.reader(data, delimiter=',')
        next(csv_data)
        for row in csv_data:
            username = row[2].split("@")
            if len(username)<=1:
                continue
            if str(row[4]).strip() == "D":
                democrats.append(username[len(username)-1])
            else:
                republicans.append(username[len(username)-1])
    return democrats, republicans

def main():
    democrats, republicans = starting_twitter_handles()
    twitter=Twitter()
    starting_users = twitter.get_users("D", democrats)
    starting_users.extend(twitter.get_users("R", republicans))
    for user in starting_users:
        print(user)

main()
