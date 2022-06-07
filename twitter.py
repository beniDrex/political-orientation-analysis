import json
import tweepy
import sys
import csv

class User:
    def __init__(self, username, id, name, political_party):
        self.username=username
        self.id=id
        self.name=name
        self.political_party=political_party
        self.tweets=[]
        self.following=[]
        # self.shared_urls=[]
    
    def __str__(self):
        return f"Username: {self.username}, Name: {self.name}, Political Party: {self.political_party}\n Tweets: {self.tweets}"

class Twitter:
    def __init__(self, auth_location="./auth.json"):
        try:
            with open(auth_location, "r") as auth_file:
                data = json.load(auth_file)
                self.bearer_token=data["bearer_token"]

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

    def scrapper(self, twitter_users, max_depth=0):
        for i, user in enumerate(twitter_users):
            user_temp_tweets=[]
            following_list=[]
            # engaged_users_object=[]
            users_tweets = self.client.get_users_tweets(user.id, exclude='replies', max_results=10)
            if users_tweets and users_tweets.data:
                for tweet in users_tweets.data:
                    user_temp_tweets.append(tweet.text)
            
            if max_depth > 0:
                users_following_resp = self.client.get_users_following(user.id, max_results=5)
                if users_following_resp and users_following_resp.data:
                    for following in users_following_resp.data:
                        user_obj=User(following.username, following.id, following.name, user.political_party)
                        following_list.append(user_obj)

            user.tweets=user_temp_tweets
            populate_user_data(user) # save row to csv
            if following_list:
                self.scrapper(following_list, max_depth-1)

            
def populate_user_data(user):
    with open('./data.csv', 'a', newline='\n') as outfile:
        csv_writer = csv.writer(outfile)
        row = [ user.username, user.name, user.political_party, user.id, str(user.tweets) ]
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
    # starting twitter handles of house representatives (https://pressgallery.house.gov/member-data/members-official-twitter-handles)
    democrats, republicans = starting_twitter_handles()
    twitter_users = twitter.get_users("D", democrats)
    twitter_users.extend(twitter.get_users("R", republicans))
    # multiple users can be scrapped per account by increasing depth 
    # Currently set to 0 since basic API key hits rate limit almost instantly if fetching followers
    # for every account that we are looping over
    populated_twitter_users = twitter.scrapper(twitter_users, max_depth=1)
    for user in populated_twitter_users:
        if user.tweets:
            print(user)

main()
