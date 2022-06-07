import json
import tweepy
import sys
from pprint import pprint
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
        return f"Username: {self.username}, Name: {self.name}, Political Party: {self.political_party}\n Tweets: {self.tweets}, Engaged Users: {self.engaged_users}"

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
        if self.client is None:
            self.client=tweepy.Client(bearer_token=self.bearer_token)

        return self.client

    def get_user_object(self, user, political_party):
        return User(user.username, user.id, user.name, political_party)

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

    def scrapper(self, twitter_users):
        for i, user in enumerate(twitter_users):
            user_temp_tweets=[]
            engaged_users=[]
            engaged_users_object=[]
            users_tweets = self.client.get_users_tweets(user.id, exclude='replies', max_results=10)
            if users_tweets and users_tweets.data:
                for index, tweet in enumerate(users_tweets.data):
                    user_temp_tweets.append(tweet.text)
                    # if index < 2:
                    liking_users = self.client.get_liking_users(tweet.id)
                    if liking_users is not None and liking_users.data is not None:
                        for liking_user in liking_users.data:
                            if liking_user.username not in engaged_users:
                                # user_obj=User(liking_user.username, liking_user.id, liking_user.name, user.political_party)
                                engaged_users.append(liking_user.username)
                                # engaged_users_object.append(user_obj)

                user.tweets=user_temp_tweets
                user.engaged_users=engaged_users

                populate_user_data(user) # save data to csv
                # if i == 4:
                #     break
                if engaged_users_object:
                    twitter_users.extend(self.scrapper(engaged_users_object))
        return twitter_users
            
            
def populate_user_data(user):
    with open('./data.csv', 'a', newline='\n') as outfile:
        csv_writer = csv.writer(outfile)
        row = [ user.username, user.name, user.political_party, user.id, str(user.tweets), str(user.engaged_users) ]
        csv_writer.writerow(row)
        

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
    # init twitter client
    twitter=Twitter()
    # init starting twitter handles (house representatives)
    democrats, republicans = starting_twitter_handles()
    twitter_users = twitter.get_users("D", democrats)
    twitter_users.extend(twitter.get_users("R", republicans))

    populated_twitter_users = twitter.scrapper(twitter_users)
    for user in populated_twitter_users:
        if user.tweets:
            print(user)
    # for user in starting_users:
    #     print(user)

main()
