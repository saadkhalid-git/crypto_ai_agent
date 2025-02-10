import tweepy
import os


def fetch_tweets(username="crypto_banter", max_results=1000):
    client = tweepy.Client(bearer_token=os.getenv("TWITTER_BEARER_TOKEN"))
    user = client.get_user(username=username)
    tweets = client.get_users_tweets(
        user.data.id,
        max_results=max_results,
        exclude=["retweets", "replies"],
        tweet_fields=["created_at"]
    )
    return [t.text for t in tweets.data]


def update_content_file():
    tweets = fetch_tweets()
    with open("data/crypto_banter_content.txt", "w") as f:
        f.write("\n".join(tweets))