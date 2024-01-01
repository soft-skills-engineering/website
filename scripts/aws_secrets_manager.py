import os.path, json, sys
import boto3

AWS_REGION_NAME = 'us-west-1'

def get_secret(secret_id):
  client = create_boto_session().client(service_name='secretsmanager')
  response = client.get_secret_value(SecretId=secret_id)
  secrets = json.loads(response['SecretString'])
  return secrets


def store_secret(secret_id, secret):
  client = create_boto_session().client(service_name='secretsmanager')
  client.update_secret(SecretId=secret_id, SecretString=json.dumps(secret))


def get_aws_credentials():
  script_path = os.path.dirname(os.path.realpath(__file__))
  auth_file = script_path + "/aws-secrets-manager-auth.json"
  if not os.path.exists(auth_file):
    sys.stderr.write("Cannot access AWS Secrets Manager: Missing file {}\n".format(auth_file))
    sys.exit(1)
  with open(auth_file) as f:
    auth = json.loads(f.read())
  if not auth.get('aws_access_key_id', '').strip():
    sys.stderr.write("Cannot access AWS Secrets Manager: Missing 'aws_access_key_id' from {}\n".format(auth_file))
    sys.exit(1)
  if not auth.get('aws_secret_access_key', '').strip():
    sys.stderr.write("Cannot access AWS Secrets Manager: Missing 'aws_secret_access_key' from {}\n".format(auth_file))
    sys.exit(1)
  return auth["aws_access_key_id"], auth["aws_secret_access_key"]


def create_boto_session():
  aws_access_key_id, aws_secret_access_key = get_aws_credentials()
  return boto3.session.Session(
      aws_access_key_id=aws_access_key_id,
      aws_secret_access_key=aws_secret_access_key,
      region_name=AWS_REGION_NAME,
  )