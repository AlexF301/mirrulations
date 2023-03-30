import os
from json import dumps, load
from mirrcore.amazon_s3 import AmazonS3
# from dotenv import load_dotenv
# import boto3


class Saver:
    """
    A class which takes the content of an attachment (pdf, doc, etc.), and
    saves it to a given path.
    ...
    Methods
    -------
    save(content = response, path = string)
        Takes the content (pdf, doc, etc.) and saves the attachment to a
        given path
    """

    def make_path(self, path):
        try:
            os.makedirs(f'/data{path}')
        except FileExistsError:
            print(f'Directory already exists in root: /data{path}')

    def save_to_disk(self, path, data):
        with open(path, 'x', encoding='utf8') as file:
            print('Writing results to disk')
            file.write(dumps(data))

    def save_json(self, path, data):
        """
        writes the results to disk. used by docket document and comment jobs

        Parameters
        ----------
        data : dict
            the results data to be written to disk
        """
        data = data['results']
        if os.path.exists(path) is False:
            self.save_to_disk(path, data)
        else:
            self.check_for_duplicates(path, data, 1)

    def save_duplicate_json(self, path, data, i):
        path_without_file_type = path.strip(".json")
        path = f'{path_without_file_type}({i}).json'
        if os.path.exists(path) is False:
            print(f'JSON is different than duplicate: Labeling ({i})')
            self.save_to_disk(path, data)
        else:
            self.check_for_duplicates(path, data, i + 1)

    def save_attachment(self, path, data):
        with open(path, "wb") as file:
            file.write(data)
            file.close()

    def open_json_file(self, path):
        with open(path, encoding='utf8') as file:
            saved_data = load(file)
        return saved_data

    def is_duplicate(self, existing, new):
        if existing == new:
            print('Data is a duplicate, skipping this download')
            return True
        return False

    def check_for_duplicates(self, path, data, i):
        if self.is_duplicate(self.open_json_file(path), data) is False:
            self.save_duplicate_json(path, data, i)

    # # Move to amazon_s3 class?
    # def establish_s3_connection(self):
    #     """
    #     Checks if a valid connection could be made to s3
    #     """
    #     load_dotenv()
    #     aws_access_key = os.getenv("AWS_ACCESS_KEY")
    #     aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    #     try:
    #         s3_client = boto3.client(
    #             's3',
    #             region_name='us-east-1',
    #             aws_access_key_id=aws_access_key,
    #             aws_secret_access_key=aws_secret_access_key
    #             )
    #         return s3_client
    #     except Exception:
    #         return False

    def save_json_to_s3(self, bucket, path, data):
        s_3 = AmazonS3(bucket)
        s_3.put_text_s3(
            path,
            data
            )
        print("SUCCESS: Wrote json to S3")

    def save_attachment_to_s3(self, bucket, path, data):
        s_3 = AmazonS3(bucket)
        s_3.put_binary_s3(
            path,
            data
            )
        print("SUCCESS: Wrote json to S3")
