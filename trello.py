import sys, json, os

BOARD_ID='Os1ByyJc'

def read_auth_info():
  script_path = os.path.dirname(os.path.realpath(__file__))
  auth_file = script_path + "/trello-auth.json"
  if not os.path.exists(auth_file):
    print("Cannot access Trello: Missing {}".format(auth_file))
    sys.exit(1)
  with open("trello-auth.json") as f:
    auth = json.loads(f.read())
  if not auth.get('key', '').strip():
    print("Cannot access Trello: Missing 'key' from {}".format(auth_file))
    sys.exit(1)
  if not auth.get('token', '').strip():
    print("Cannot access Trello: Missing 'token' from {}".format(auth_file))
    sys.exit(1)
  return auth['key'], auth['token']

def set_up():
  if len(sys.argv) != 2:
    print("Usage: {} <episode-number>".format(sys.argv[0]))
    sys.exit(1)
  episode_number = sys.argv[1]
  key, token = read_auth_info()
  return episode_number, key, token

def get_question_cards(key, token, episode_number):
  import requests
  list_id = find_episode_list_id(key, token, episode_number)
  if not list_id:
    print("Could not find Trello list for episode {}".format(episode_number))
    sys.exit(1)
  response = requests.get('https://api.trello.com/1/lists/{}/cards?key={}&token={}'.format(list_id, key, token))
  cards = json.loads(response.content)
  question_cards = [card for card in cards if any(label['name'] == 'question' for label in card['labels'])]
  return question_cards
  #for card in cards:
  #  if lst['name'].lower() == "episode {}".format(episode_number):
  #    return lst['id']

def find_episode_list_id(key, token, episode_number):
  import requests
  response = requests.get('https://api.trello.com/1/boards/{}/lists?key={}&token={}'.format(BOARD_ID, key, token))
  lists = json.loads(response.content)
  for lst in lists:
    if lst['name'].lower() == "episode {}".format(episode_number):
      return lst['id']
