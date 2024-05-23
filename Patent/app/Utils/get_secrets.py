import json
import os
import boto3
from botocore.exceptions import ClientError


def get_and_set_secrets():
    secret_name = "patentgenie-ml-env"
    region_name = "us-east-1"
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # Handle the exception as required and exit
        print(f"Unable to retrieve secret: {e}")
        raise e
    else:
        # Assuming the secret is stored as a JSON string
        secret = get_secret_value_response["SecretString"]
        secret = json.loads(secret)
        # Extracting specific secrets and setting them as environment variables
        os.environ["OPENAI_API_KEY"] = secret.get("OPENAI_API_KEY", "")
        os.environ["OPENAI_ORG_KEY"] = secret.get("OPENAI_ORG_KEY", "")
        os.environ["AWS_BUCKET_NAME"] = secret.get("AWS_BUCKET_NAME", "")
        os.environ["AWS_SECRET_KEY_LOCAL"] = secret.get("AWS_SECRET_KEY_LOCAL", "")
        os.environ["AWS_ACCESS_KEY_LOCAL"] = secret.get("AWS_ACCESS_KEY_LOCAL", "")
        os.environ["MONGO_URI"] = secret.get("MONGO_URI", "")

