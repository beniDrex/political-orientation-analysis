## How to
1. Update bearer_token in auth.json with your token from [Twitter Developer Platform](https://developer.twitter.com)
2. Install required modules (tweepy)
3. Run `python3 ./twitter.py`

## Data Set
1. username - string
2. name - string
3. party - D/R
4. id - int
5. tweets - list[string]

## Challenges
- Getting elevated access to twitter API
- Managing Rate Limiting with twitter API when using a wrapper module
- A lot more bots than anticipated 

### Where the data comes from

Official twitter profiles of house representatives served as a starting point for my data. I scraped the usernames and party affiliation from https://pressgallery.house.gov/member-data/members-official-twitter-handles which served as a starting point.
By specifying max_depth and using a recursive scrapper we can fetch twitter profiles n levels deep from the starting accounts (house representatives). Multiple variables like tweet liked by, retweeted by, number of tweets liked a user, etc. can be used to more efficiently predict whether a nested profile is along the same party lines of the parent profile. However, due to strict rate limiting of Twitter API I relied on Followers to determine relevant twitter profiles
