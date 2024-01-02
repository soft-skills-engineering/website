import patreon
import requests
import json
import os.path
import sys
from datetime import datetime, timedelta
from aws_secrets_manager import get_secret, store_secret

PATREON_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'
SECRET_NAME = 'patreon_api_credentials'
WEEKLY_SHOUTOUT_MINIMUM_CENTS = 2000
ONE_TIME_SHOUTOUT_MINIMUM_CENTS = 1000


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
  response = requests.get('https://www.patreon.com/api/oauth2/api/current_user/campaigns', headers={'Authorization': f'Bearer {access_token}'})
  response.raise_for_status()
  payload = response.json()
  assert len(payload['data']) == 1
  campaign = payload['data'][0]
  campaign_id = campaign['id']
  return campaign_id


def get_slack_invite_emails(access_token):
  all_members = get_all_members(access_token)
  cutoff_datetime = datetime.utcnow() - timedelta(days=60)
  recent_members = [member for member in all_members
                    if member['pledge_relationship_start'] > cutoff_datetime
                    and member['last_charge_status'] == 'Paid'
                    and member['currently_entitled_amount_cents'] > 0]
  return [recent_member['email'] for recent_member in recent_members]


def get_shoutouts(access_token):
  from pprint import pprint
  first_of_the_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()
  all_members = get_all_members(access_token)
  for member in all_members:
    member['start_month'] = member['pledge_relationship_start'].replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()
  weekly_shout_outs = [member for member in all_members if member['currently_entitled_amount_cents'] >= WEEKLY_SHOUTOUT_MINIMUM_CENTS]
  one_time_shout_outs = [member for member in all_members
                         if ONE_TIME_SHOUTOUT_MINIMUM_CENTS <= member['currently_entitled_amount_cents'] < WEEKLY_SHOUTOUT_MINIMUM_CENTS
                         and member['campaign_lifetime_support_cents'] == member['currently_entitled_amount_cents']
                         and member['start_month'] == first_of_the_month]
  weekly_shout_outs = sorted(weekly_shout_outs, key=lambda member: (member['currently_entitled_amount_cents'], member['pledge_relationship_start']), reverse=True)
  one_time_shout_outs = sorted(one_time_shout_outs, key=lambda member: (member['currently_entitled_amount_cents'], member['pledge_relationship_start']), reverse=True)
  return weekly_shout_outs, one_time_shout_outs


def get_all_members(access_token):
  campaign_id = get_patreon_campaign_id(access_token)
  url = f'https://www.patreon.com/api/oauth2/v2/campaigns/{campaign_id}/members?page[count]=200&fields[member]=full_name,email,last_charge_date,last_charge_status,currently_entitled_amount_cents,patron_status,pledge_relationship_start,campaign_lifetime_support_cents'
  all_members = []
  while url is not None:
    response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
    payload = response.json()
    members = payload['data']
    for raw_member in members:
      member = raw_member['attributes'].copy()
      member['pledge_relationship_start'] = parse_patreon_datetime(member['pledge_relationship_start'])
      member['last_charge_date'] = parse_patreon_datetime(member['last_charge_date'])
      all_members.append(member)
    url = payload.get('links', {}).get('next')
  return all_members


def parse_patreon_datetime(datetime_string):
  if datetime_string is None:
    return None
  dt = datetime.strptime(datetime_string, PATREON_DATETIME_FORMAT)
  dt = dt.replace(tzinfo=None)
  return dt