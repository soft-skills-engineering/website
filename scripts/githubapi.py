from github import Github
import os.path, json, sys

REPO_FULL_PATH='soft-skills-engineering/website'
PULL_REQUEST_URL_TEMPLATE = 'https://github.com/{repo_full_path}/pull/{pull_request_number}'

def create_github_client():
  return Github(read_auth_token())

def read_auth_token():
  script_path = os.path.dirname(os.path.realpath(__file__))
  auth_file = script_path + "/github-auth.json"
  if not os.path.exists(auth_file):
    sys.stderr.write("Cannot access GitHub: Missing {}\n".format(auth_file))
    sys.stderr.write("Create a Personal Access Token token with 'repo' scope if you don't already have one: https://github.com/settings/tokens\n")
    sys.exit(1)
  with open("github-auth.json") as f:
    auth = json.loads(f.read())
  if not auth.get('token', '').strip():
    sys.stderr.write("Cannot access GitHub: Missing 'token' from {}\n".format(auth_file))
    sys.exit(1)
  return auth['token']

def create_pull_request(github_client, episode_number, episode_mp3_url):
  repo = github_client.get_repo(REPO_FULL_PATH)
  pull_request = repo.create_pull(
    title='Episode {}'.format(episode_number),
    head='episode-{}'.format(episode_number),
    body='🎉 This is episode {episode_number}.\n\nPreview it here: [{episode_mp3_url}]({episode_mp3_url})\n\nAfter listening to the episode, merge this PR to publish the episode. It will go live within 5 minutes when GitHub publishes the new code.'
        .format(
            episode_number=episode_number,
            episode_mp3_url=episode_mp3_url),
    base='gh-pages',
    maintainer_can_modify=True,
  )

  pull_request.set_labels('episode')

  pull_request_url = PULL_REQUEST_URL_TEMPLATE.format(
    repo_full_path=REPO_FULL_PATH,
    pull_request_number=pull_request.number,
  )

  return pull_request_url
