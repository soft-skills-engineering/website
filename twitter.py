import os.path, json, tweepy

def tweet(api, episode_number, episode_summary, episode_url):
  TWEET_TEMPLATE="Episode {episode_number}: {episode_summary}\n\n{episode_url}"
  tweet_content = TWEET_TEMPLATE.format(
          episode_number=episode_number,
          episode_summary=episode_summary,
          episode_url=episode_url)

  tweet = api.update_status(tweet_content)

  tweet_url = 'https://twitter.com/{screen_name}/status/{tweet_id}'.format(
          screen_name=tweet.author.screen_name,
          tweet_id=tweet.id)

  return tweet_url, tweet_content

def twitter_api():
  REQUIRED_AUTH_FIELDS = ['consumer_token', 'consumer_secret', 'access_token', 'access_token_secret']

  script_path = os.path.dirname(os.path.realpath(__file__))
  auth_file = script_path + "/twitter-auth.json"
  if not os.path.exists(auth_file):
    sys.stderr.write("Cannot access Twitter: Missing {}\n".format(auth_file))
    sys.exit(1)
  with open("twitter-auth.json") as f:
    auth_json = json.loads(f.read())

  missing_fields = [x for x in REQUIRED_AUTH_FIELDS if not auth_json.get(x, '').strip()]
  if missing_fields:
    sys.stderr.write("Cannot access Twitter: Missing field{} {} from {}\n".format(
        's' if len(missing_fields) > 1 else '',
        ', '.join(missing_fields),
        reqauth_file),
    )
    sys.exit(1)

  auth = tweepy.OAuthHandler(auth_json['consumer_token'], auth_json['consumer_secret'])
  auth.set_access_token(auth_json['access_token'], auth_json['access_token_secret'])
  api = tweepy.API(auth)
  return api
