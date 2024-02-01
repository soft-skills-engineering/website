import sys, json, os, re
from pprint import pprint
from datetime import datetime
from patreon_api import get_shoutouts, get_patreon_access_token
import requests

BOARD_ID_SHORT = 'Os1ByyJc'
BOARD_ID_LONG  = '56d5bc8b5f9c1b7d798e04ee'
TEMPLATE_LIST_NAME = 'Episode Template'
SOURE_URL = 'https://github.com/soft-skills-engineering/website/blob/gh-pages/scripts/trello-setup-next-episode'

# IDs of hosts, so we can alternate who is assigned to each card
ASSIGNEE_IDS = ['4f07a508dc4ba55307159c68', '4f07b31df58973cd020694fe']
assert len(ASSIGNEE_IDS) == 2 # the logic in this script assumes exactly two hosts

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


def create_next_episode_list_if_needed(key, token):
  print(f'Getting most recent episode from Trello...')
  most_recent_episode_number, most_recent_episode_list_id = find_most_recent_episode_list(key, token)

  # Need to create a new card?
  if is_episode_list_already_done(key, token, most_recent_episode_list_id):
    episode_number_to_set_up = most_recent_episode_number + 1
    print(f'Creating episode Trello list for episode {episode_number_to_set_up}')
    episode_list = create_episode_list_from_template(key, token, episode_number_to_set_up, most_recent_episode_list_id)
    populate_next_episode_list(key, token, episode_list, most_recent_episode_list_id)
  else:
    print(f'Not creating a new Trello list, because episode {most_recent_episode_number} still needs to be finished')


def find_most_recent_episode_list(key, token):
  current_lists = get_json(f'https://api.trello.com/1/boards/{BOARD_ID_SHORT}/lists?key={key}&token={token}')
  most_recent_episode_number = 0
  most_recent_episode_list_id = None
  for lst in current_lists:
    matches = re.search(r'episode (\d+)', lst['name'].lower())
    if matches:
      episode_number = int(matches.group(1))
      if episode_number > most_recent_episode_number:
        most_recent_episode_number = episode_number
        most_recent_episode_list_id = lst['id']
  return most_recent_episode_number, most_recent_episode_list_id


def get_template_list_id(key, token):
  lists = get_json(f'https://api.trello.com/1/boards/{BOARD_ID_SHORT}/lists?key={key}&token={token}')
  for lst in lists:
    if lst['name'].strip().lower() == TEMPLATE_LIST_NAME.strip().lower():
      return lst['id']
  return None


def populate_next_episode_list(key, token, episode_list, most_recent_episode_list_id):
  episode_list_id = episode_list['id']
  created_cards = get_json(f'https://api.trello.com/1/lists/{episode_list_id}/cards?key={key}&token={token}')
  print(f'Created list for episode with {len(created_cards)} cards')
  append_source_card(key, token, episode_list_id)
  populate_patreon_shoutouts(key, token, created_cards)
  assign_hosts_to_cards(key, token, created_cards, most_recent_episode_list_id)


def append_source_card(key, token, episode_list_id):
  payload = {
    'name': f'This list was created by a 🤖',
    'desc': f'Find the script at {SOURE_URL}',
  }
  post_json(payload, f'https://api.trello.com/1/lists/{episode_list_id}/cards?key={key}&token={token}')


def create_episode_list_from_template(key, token, episode_number, most_recent_episode_list_id):
  list_name = f'Episode {episode_number}'
  template_list_id = get_template_list_id(key, token)
  list_payload = {
    'name': list_name,
    'idBoard': BOARD_ID_LONG,
    'idListSource': template_list_id,
    'pos': 'top',
  }
  created_list = post_json(list_payload, f'https://api.trello.com/1/lists?key={key}&token={token}')
  return created_list


def assign_hosts_to_cards(key, token, created_cards, most_recent_episode_list_id):
  print('Assigning hosts to each card...')
  # Assign host to the intro for the next episode
  previous_episode_cards = get_json(f'https://api.trello.com/1/lists/{most_recent_episode_list_id}/cards?key={key}&token={token}')
  previous_episode_intro_card = find_intro_card(previous_episode_cards)
  previous_intro_assignee = previous_episode_intro_card['idMembers'][0]

  next_episode_intro_assignee = [id for id in ASSIGNEE_IDS if id != previous_intro_assignee][0]
  next_episode_intro_card = find_intro_card(created_cards)
  assign_member_to_card(key, token, next_episode_intro_card['id'], next_episode_intro_assignee)
  next_assignee = previous_intro_assignee
  for card in created_cards:
    if is_question_card(card) or is_patreon_card(card):
      assign_member_to_card(key, token, card['id'], next_assignee)
      next_assignee = [id for id in ASSIGNEE_IDS if id != next_assignee][0]

def populate_patreon_shoutouts(key, token, created_cards):
  print('Adding Patreon shoutouts...')
  patreon_card = [card for card in created_cards if is_patreon_card(card)][0]
  weekly_shoutouts, one_time_shoutouts = get_shoutouts(get_patreon_access_token())

  shoutout_string = f'{len(one_time_shoutouts)} one-time shoutouts:\n\n'
  for one_time_shoutout in one_time_shoutouts:
    shoutout_string += f' * {one_time_shoutout["full_name"]}\n'
  shoutout_string += '\n\n'

  shoutout_string += f'{len(weekly_shoutouts)} weekly shoutouts:'
  shoutout_string += '\n\n'
  for weekly_shout_out in weekly_shoutouts:
    shoutout_string += f' * {weekly_shout_out["full_name"]}\n\n'
  shoutout_string += '\n\n'

  patreon_card['name'] = f'Patrons as of {datetime.now().date()}'
  patreon_card['desc'] = shoutout_string
  put_json(patreon_card, f'https://api.trello.com/1/cards/{patreon_card["id"]}?key={key}&token={token}')

  print(f'Added {len(weekly_shoutouts)} weekly shoutouts and {len(one_time_shoutouts)} one-time shoutouts to Trello card...')


def is_question_card(card):
  return 'question' in [label['name'] for label in card['labels']]


def is_patreon_card(card):
  return 'patreon' in [label['name'] for label in card['labels']]


def assign_member_to_card(key, token, card_id, member_id):
  payload = {
    'value': member_id,
  }
  post_json(payload, f'https://api.trello.com/1/cards/{card_id}/idMembers?key={key}&token={token}')


def find_intro_card(cards):
  for card in cards:
    if 'intro' in [label['name'] for label in card['labels']]:
      return card
  assert False, 'Could not find intro card for episode'


def is_episode_list_already_done(key, token, list_id):
  episode_cards = get_json(f'https://api.trello.com/1/lists/{list_id}/cards?key={key}&token={token}')
  completed_question_cards = [
    card for card in episode_cards
    if 'question' in [label['name'] for label in card['labels']]
       and card['name'].lower() not in ('q1', 'q2')
  ]

  is_episode_list_setup = len(completed_question_cards) >= 2
  return is_episode_list_setup


def find_episode_list_id(key, token, episode_number):
  lists = get_json('https://api.trello.com/1/boards/{}/lists?key={}&token={}'.format(BOARD_ID_SHORT, key, token))
  for lst in lists:
    # FIXME Using `startswith` will break at episode 1000 since it will match episode 100.
    #       At current weekly cadence, this will break in the year 2034.
    if lst['name'].lower().startswith("episode {}".format(episode_number)):
      return lst['id']


def put_json(payload, url):
  return put_or_post_json('put', payload, url)

def post_json(payload, url):
  return put_or_post_json('post', payload, url)

def put_or_post_json(put_or_post, payload, url):
  if put_or_post == 'put':
    response = requests.put(url, json=payload)
  elif put_or_post == 'post':
    response = requests.post(url, json=payload)
  else:
    raise ValueError(f'Invalid value for put_or_post. Expected "put" or "post", but got: "{put_or_post}"')
  if response.status_code != 200:
    sys.stderr.write("Got error from Trello API. HTTP status code: {}, response content: {}\n".format(response.status_code, response.content))
    sys.exit(1)
  return response.json()


def get_json(url):
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
