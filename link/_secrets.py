import base64
import json


SECRETS_SERVICE = "secretsmanager"
DEFAULT_REGION = "us-east-1"


def get_secret(key):

    import boto3
    from botocore.exceptions import ClientError, NoRegionError


    session = boto3.session.Session()
    try:
        client = session.client(service_name=SECRETS_SERVICE)
    except NoRegionError:
        print("Warning, no default region set, defaulting to us-east-1. Please set a default region in either your aws config file or via environment variable AWS_DEFAULT_REGION")
        client = session.client(service_name=SECRETS_SERVICE, region_name=DEFAULT_REGION)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=key)

    except Exception as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        else:
            raise e
    else:
        if 'SecretString' in get_secret_value_response:
            return  json.loads(get_secret_value_response['SecretString'])
        else:
            return json.loads(base64.b64decode(get_secret_value_response['SecretBinary']))


