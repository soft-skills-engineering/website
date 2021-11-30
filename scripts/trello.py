import sys, json, os

BOARD_ID='Os1ByyJc'

def read_auth_info():
  script_path = os.path.dirname(os.path.realpath(__file__))
  auth_file = script_path + "/trello-auth.json"
  if not os.path.exists(auth_file):
    sys.stderr.write("Cannot access Trello: Missing {}\n".format(auth_file))
    sys.exit(1)
  with open(auth_file) as f:
    auth = json.loads(f.read())
  if not auth.get('key', '').strip():
    sys.stderr.write("Cannot access Trello: Missing 'key' from {}\n".format(auth_file))
    sys.exit(1)
  if not auth.get('token', '').strip():
    sys.stderr.write("Cannot access Trello: Missing 'token' from {}\n".format(auth_file))
    sys.exit(1)
  return auth['key'], auth['token']

def set_up():
  if len(sys.argv) != 2:
    sys.stderr.write("Usage: {} <episode-number>\n".format(sys.argv[0]))
    sys.exit(1)
  episode_number = sys.argv[1]
  key, token = read_auth_info()
  return episode_number, key, token

def get_cards(key, token, episode_number):
  list_id = find_episode_list_id(key, token, episode_number)
  if not list_id:
    sys.stderr.write("Could not find Trello list for episode {}\n".format(episode_number))
    sys.exit(1)
  return get_json('https://api.trello.com/1/lists/{}/cards?key={}&token={}'.format(list_id, key, token))

def get_cards_by_label(key, token, episode_number, label_to_find):
  cards = get_cards(key, token, episode_number)
  return [card for card in cards if any(label['name'] == label_to_find for label in card['labels'])]

def get_question_cards(key, token, episode_number):
  return get_cards_by_label(key, token, episode_number, label_to_find='question')

# assuming there is only a single note card if it exists
def get_show_notes(key, token, episode_number):
  show_notes = get_cards_by_label(key, token, episode_number, label_to_find='notes')
  return show_notes[0]['desc'] if len(show_notes) > 0 else ''

def find_episode_list_id(key, token, episode_number):
  lists = get_json('https://api.trello.com/1/boards/{}/lists?key={}&token={}'.format(BOARD_ID, key, token))
  for lst in lists:
    # FIXME Using `startswith` will break at episode 1000 since it will match episode 100.
    #       At current weekly cadence, this will break in the year 2034.
    if lst['name'].lower().startswith("episode {}".format(episode_number)):
      return lst['id']

def get_json(url):
  import requests
  response = requests.get(url)
  if response.status_code == 200:
    try:
      return json.loads(response.content)
    except json.decoder.JSONDecodeError as e:
      sys.stderr("Invalid JSON returned from Trello API: {}, JSON: {}".format(e, response.content))
      sys.exit(1)
  else:
    sys.stderr.write("Got error from Trello API. HTTP status code: {}, response content: {}\n".format(response.status_code, response.content))
    sys.exit(1)
