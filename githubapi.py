from github import Github
import os.path, json

REPO_FULL_PATH='soft-skills-engineering/website'
PULL_REQUEST_URL_TEMPLATE = 'https://github.com/{repo_full_path}/pull/{pull_request_number}'

def create_github_client():
    return Github(read_auth_token())

def read_auth_token():
  script_path = os.path.dirname(os.path.realpath(__file__))
  auth_file = script_path + "/github-auth.json"
  if not os.path.exists(auth_file):
    print("Cannot access GitHub: Missing {}".format(auth_file))
    print("Create a Personal Access Token token with 'repo' scope if you don't already have one: https://github.com/settings/tokens")
    sys.exit(1)
  with open("github-auth.json") as f:
    auth = json.loads(f.read())
  if not auth.get('token', '').strip():
    print("Cannot access GitHub: Missing 'token' from {}".format(auth_file))
    sys.exit(1)
  return auth['token']

def create_pull_request(github_client, episode_number):
  repo = github_client.get_repo(REPO_FULL_PATH)
  pull_request = repo.create_pull(
    title='Episode {}'.format(episode_number),
    head='episode-{}'.format(episode_number),
    body='This is episode {} 🎉'.format(episode_number),
    base='gh-pages',
    maintainer_can_modify=True,
  )
  pull_request_url = PULL_REQUEST_URL_TEMPLATE.format(
    repo_full_path=REPO_FULL_PATH,
    pull_request_number=pull_request.number,
  )

  issue = repo.get_issue(pull_request.number)
  issue.edit(labels=['episode'])

  return pull_request_url
