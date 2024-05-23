import os
import boto3
import traceback
from botocore.config import Config

from app.services.mongo_service import get_mongo_connection, close_mongo_connection
from bson.objectid import ObjectId
from app.Utils.get_secrets import get_and_set_secrets

get_and_set_secrets()

# from dotenv import load_dotenv
#
# load_dotenv()

s3Client = boto3.resource(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_LOCAL"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY_LOCAL"),
)

s3_upload_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_LOCAL"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY_LOCAL"),
    region_name="us-east-1",
    config=Config(signature_version='s3v4')
)

bucket_name = os.getenv("AWS_BUCKET_NAME")


def download_file_from_s3(object_key, folder_path, file_name):
    try:
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, file_name)

        s3Client.Object(bucket_name, object_key).download_file(file_path)

        print(f"File downloaded: {file_path}")
        return file_path
    except Exception as err:
        print(err, traceback.format_exc())
        return None


# Get files from S3 bucket
def get_patent_file(file_types, patent_id):
    db = get_mongo_connection()

    try:
        patent_folder_path = os.path.join("temp", patent_id)

        if os.path.exists(patent_folder_path) and os.listdir(patent_folder_path):
            print(f"Files for patent {patent_id} already downloaded.")
            return patent_folder_path
        else:
            os.makedirs(patent_folder_path, exist_ok=True)

            patent = db.patents.find_one({"_id": ObjectId(patent_id)})
            if patent is None:
                print(f"No patent found with name {patent_id}")
                return None

            for file_type in file_types:
                if file_type not in patent:
                    print(f"No {file_type} file found for {patent_id}")
                    continue

                s3_url = patent[file_type]["s3Url"]
                file_extension = patent[file_type]["fileExtension"]
                download_path = patent_folder_path

                if (
                    file_type == "customTemplate"
                ):  # Use the correct file type identifier
                    download_path = os.path.join(patent_folder_path, "custom_template")
                    os.makedirs(download_path, exist_ok=True)

                file_name = f"input_{file_type}.{file_extension}"
                file_path = os.path.join(download_path, file_name)

                download_file_from_s3(s3_url, download_path, file_name)
                print(
                    f"File for {file_type} downloaded successfully in {download_path}."
                )

            return patent_folder_path
    except Exception as err:
        print(err, traceback.format_exc())
    finally:
        if "db" in locals():
            close_mongo_connection(db.client)


# Upload file to S3 bucket
def upload_file_to_s3(local_file, patent_id):
    file_path = os.path.join("Upload_File", patent_id, local_file)
    s3_folder = os.path.join("Document_to_download", patent_id)
    s3_file_key = os.path.join(s3_folder, local_file).replace("\\", "/")
    try:
        s3_upload_client.upload_file(file_path, bucket_name, s3_file_key)
        file_url = s3_upload_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket_name,
                "Key": s3_file_key,
                "ResponseContentType": "application/octet-stream",
            },
            ExpiresIn=3600,
        )
        print(f"File uploaded to S3: {file_url}")

        return file_url, local_file
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
