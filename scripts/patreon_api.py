import patreon
import requests
import json
import os.path
import sys
from pprint import pprint

from aws_secrets_manager import get_secret, store_secret

SECRET_NAME = 'patreon_api_credentials'

def test():
  access_token = get_patreon_access_token()
  get_shoutout_list(access_token)

def get_patreon_access_token():
  script_path = os.path.dirname(os.path.realpath(__file__))
  auth_file = script_path + "/patreon-auth.json"
  if not os.path.exists(auth_file):
    sys.stderr.write("Cannot access Patreon credentials: Missing file {}\n".format(auth_file))
    sys.exit(1)
  with open(auth_file) as f:
    auth = json.loads(f.read())
  if not auth.get('patreon_client_id', '').strip():
    sys.stderr.write("Cannot access Patreon credentials: Missing 'patreon_client_id' from {}\n".format(auth_file))
    sys.exit(1)
  if not auth.get('patreon_client_secret', '').strip():
    sys.stderr.write("Cannot access Patreon credentials: Missing 'patreon_client_secret' from {}\n".format(auth_file))
    sys.exit(1)
  patreon_client_id = auth["patreon_client_id"]
  patreon_client_secret = auth["patreon_client_secret"]
  return refresh_patreon_access_token(patreon_client_id, patreon_client_secret)


def refresh_patreon_access_token(patreon_client_id, patreon_client_secret):
  patreon_secrets = get_secret(SECRET_NAME)
  auth_url = 'https://www.patreon.com/api/oauth2/token'
  response = requests.post(
    auth_url,
    headers={
      'Conent-Type': 'application/x-www-form-urlencoded'
    },
    data = {
      'grant_type': 'refresh_token',
      'refresh_token': patreon_secrets['patreon_api_refresh_token'],
      'client_id': patreon_client_id,
      'client_secret': patreon_client_secret,
    },
  )

  if response.status_code != 200:
    message = f'Could not get a new access/refresh token from Patreon API: {response.status_code}: {response.text}'
    raise ValueError(message)

  payload = response.json()
  new_access_token = payload['access_token']
  new_refresh_token = payload['refresh_token']

  # Store the new tokens for next time, since they change every time we authenticate
  store_secret(SECRET_NAME, {
    "patreon_api_access_token": new_access_token,
    "patreon_api_refresh_token": new_refresh_token,
  })

  return new_access_token

def get_patreon_campaign_id(access_token):
  print('Getting campaign ID')
  response = requests.get('https://www.patreon.com/api/oauth2/api/current_user/campaigns', headers={'Authorization': f'Bearer {access_token}'})
  response.raise_for_status()
  payload = response.json()
  assert len(payload['data']) == 1
  campaign = payload['data'][0]
  campaign_id = campaign['id']
  print(f'Got campaign ID: {campaign_id}')
  return campaign_id


def get_shoutout_list(access_token):
  campaign_id = get_patreon_campaign_id(access_token)
  response = requests.get(f'https://www.patreon.com/api/oauth2/api/campaigns/{campaign_id}/pledges?include=patron.user.email&fields[user]=email', headers={'Authorization': f'Bearer {access_token}'})
  pprint(response.json())
  return


if __name__ == '__main__':
  test()