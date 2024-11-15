import os
import time
import tweepy
from anthropic import Anthropic
from datetime import datetime
import schedule
from typing import List
from dotenv import load_dotenv
import random
 
class TwitterClaudeBot:
    def __init__(self, anthropic_api_key: str, twitter_api_key: str, twitter_api_secret: str, 
                 twitter_access_token: str, twitter_access_token_secret: str, tweets: list):
        # Initialize Anthropic client
        self.anthropic = Anthropic(api_key=anthropic_api_key)
 
        # Initialize Twitter client
        auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
        auth.set_access_token(twitter_access_token, twitter_access_token_secret)
        self.twitter = tweepy.Client(
            consumer_key=twitter_api_key,
            consumer_secret=twitter_api_secret,
            access_token=twitter_access_token,
            access_token_secret=twitter_access_token_secret
        )
 
        # Initialize predefined tweets - filtered for appropriate content
        self.predefined_tweets = tweets
        self.current_tweet_index = 0
    
    def generate_tweet(self) -> str:
        """Get next tweet from predefined list or generate using Claude if list is exhausted"""
        if self.current_tweet_index < len(self.predefined_tweets):
            tweet = self.predefined_tweets[self.current_tweet_index]
            self.current_tweet_index += 1
            return tweet
 
        # If we've used all predefined tweets, generate using Claude
        base_tweet = random.choice(self.predefined_tweets)
        prompt = f"""Based on the following tweet, generate a single engaging tweet about an interesting fact, insight, or observation.
        Keep it under 280 characters and have same hashtag.
        Make it thoughtful and interesting enough that people would want to share it. 
        Don't include description about output ex: Here's ...
        {base_tweet}
        """
        response = self.anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return response.content[0].text
 
    def post_tweet(self):
        """Post tweet automatically without requiring approval"""
        tweet_content = self.generate_tweet()
        try:
            # self.twitter.create_tweet(text=tweet_content)
            # print(f"Tweet posted successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:")
            # print("-" * 50)
            print(tweet_content)
            print("-" * 50)
        except Exception as e:
            print(f"Error posting tweet: {e}")

def read_lines_from_file(filename: str) -> list:
    """Read lines from a text file and store them in a list."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file if line.strip()]  # Remove whitespace and skip empty lines
        return lines
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
 
def main():
    # Load environment variables or prompt for them
    load_dotenv()
    anthropic_key = os.getenv('ANTHROPIC_API_KEY') or input("Enter your Anthropic API key: ")
    twitter_api_key = os.getenv('TWITTER_API_KEY') or input("Enter your Twitter API key: ")
    twitter_api_secret = os.getenv('TWITTER_API_SECRET') or input("Enter your Twitter API secret: ")
    twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN') or input("Enter your Twitter access token: ")
    twitter_access_secret = os.getenv('TWITTER_ACCESS_SECRET') or input("Enter your Twitter access token secret: ")
    
    # Load Predefined Tweets
    f_pretweets = os.getenv('PREDEFINED_TWEETS') or input("predefined_tweets.txt")
    pretweets = read_lines_from_file(f_pretweets)
    
    # Initialize bot
    bot = TwitterClaudeBot(
        anthropic_key,
        twitter_api_key,
        twitter_api_secret,
        twitter_access_token,
        twitter_access_secret,
        pretweets
    )
 
    # Schedule tweet posting every hour at the start of the hour
    # schedule.every().hour.at(":00").do(bot.post_tweet)
    schedule.every(3).seconds.do(bot.post_tweet)
 
    # Post first tweet immediately
    bot.post_tweet()
 
    # print("Bot initialized! Will post tweets every hour on the hour.")
    # print("Press Ctrl+C to exit.")
 
    # Run continuously
    while True:
        schedule.run_pending()
        # time.sleep(60)
        time.sleep(1)
 
if __name__ == "__main__":
    main()
 