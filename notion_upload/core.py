import mimetypes
import requests # type: ignore
import pprint
import os
import re
class FileTooLargeError(Exception):
    pass
n_upload_url = "https://api.notion.com/v1/file_uploads"

class base_upload:
    def __init__(self, file_path, file_name, api_key, enforce_max_size=True):
        self.file_path = file_path
        self.file_name = file_name
        self.api_key = api_key
        self.enforce_max_size = enforce_max_size
        self.mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    def validate(self):
        if self.enforce_max_size and os.path.isfile(self.file_path):
            max_bytes = 5 * 1024 * 1024  # 5MB
            file_size = os.path.getsize(self.file_path)
            if file_size > max_bytes:
                raise FileTooLargeError(
                    f"File '{self.file_path}' is {file_size / (1024 * 1024):.2f}MB, which exceeds the 5MB Notion limit."
                )
        errors = []

        if self.api_key == "your_notion_key":
            errors.append("Please set your Notion API key in the code with the variable 'NOTION_KEY'.")

        if not self.file_name:
            errors.append("Please set the file name in the code with the variable 'file_name'.")

        if mimetypes.guess_type(self.file_name)[0] != self.mime_type:
            errors.append("Your file's file extension does not match the file type. Please check the file name and try again.")

        if errors:
            print("The following issues were found:")
            for error in errors:
                print("-", error)
            return False
        return True

class internal_upload(base_upload):
    def __init__(self, file_path, file_name, api_key, enforce_max_size=True):
        super().__init__(file_path, file_name, api_key, enforce_max_size)
    def singleUpload(self):
        """
        Upload a single file to Notion.
        """
        if not self.validate():
            return
        # Start the upload
        payload = {
            "filename": self.file_name,
            "content_type": self.mime_type
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2022-06-28"
        }

        response = requests.post(n_upload_url, json=payload, headers=headers)

        if response.status_code == 200:
            file_id = response.json().get("id")
            print("Upload successfuly started! File ID: " + file_id)
        else:
            print("Upload failed:", response.status_code, response.text)
            file_id = None

        if file_id is not None:
            try:
                with open(self.file_path, "rb") as f:
                    files = {
                        "file": (self.file_name, f, self.mime_type)
                    }

                    upload_url = f"https://api.notion.com/v1/file_uploads/{file_id}/send"
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Notion-Version": "2022-06-28"
                    }

                    response = requests.post(upload_url, headers=headers, files=files)

                    if response.status_code == 200:
                        print("Upload successful! File ID: " + file_id)
                    else:
                        print("Upload failed at file send stage:", response.status_code, response.text)
            except FileNotFoundError:
                print(f"File not found: {self.file_path}")


class external_upload(base_upload):
    def __init__(self, file_path, file_name, api_key, enforce_max_size=True):
        super().__init__(file_path, file_name, api_key, enforce_max_size)
    def singleUpload(self):
        """
        Upload a single file to Notion.
        """
        if not self.validate():
            return
        #Start the upload
        payload = {
                "filename": self.file_name,  
                "content_type": self.mime_type
            }    
        headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "Notion-Version": "2022-06-28"
            }

        response = requests.post(n_upload_url, json=payload, headers=headers)

        if response.status_code == 200:
            file_id = response.json().get("id")
            print("Upload successfuly started! File ID: " + file_id)
        else:
            print("Upload failed:", response.status_code, response.text)
            file_id = None

        # Download the file from the URL       
        file_url = self.file_path
        try:
            if self.enforce_max_size:
                head_resp = requests.head(file_url)
                content_length = head_resp.headers.get("Content-Length")
                if content_length and int(content_length) > 5 * 1024 * 1024:
                    raise FileTooLargeError(
                        f"File at URL '{file_url}' is {int(content_length) / (1024 * 1024):.2f}MB, which exceeds the 5MB Notion limit."
                    )
            response = requests.get(file_url, stream=True)
            if response.status_code == 200:
                temp_file_path = f"temp_{self.file_name}"
                with open(temp_file_path, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)

                with open(temp_file_path, "rb") as f:
                    files = {
                        "file": (self.file_name, f, self.mime_type),
                    }

                    url = f"https://api.notion.com/v1/file_uploads/{file_id}/send"
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Notion-Version": "2022-06-28"
                    }

                    response = requests.post(url, headers=headers, files=files)
                    pprint.pprint(response.json())

                # Delete the temporary file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            else:
                print("Failed to download the file:", response.status_code)
        except requests.RequestException as e:
            print("Failed to download the file due to a network error:", e)

class notion_upload:
    def __init__(self, file_path, file_name, api_key, enforce_max_size=True):
        self.file_path = file_path
        self.file_name = file_name
        self.api_key = api_key
        self.enforce_max_size = enforce_max_size
        self.mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    def upload(self):
        if re.match(r'^(http|https)://', self.file_path):
            external_upload(self.file_path, self.file_name, self.api_key, self.enforce_max_size).singleUpload()
        else:
            internal_upload(self.file_path, self.file_name, self.api_key, self.enforce_max_size).singleUpload()