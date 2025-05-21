import mimetypes
import requests
import os
import re
import tempfile
import json
#Cache MIME types in memory
def _load_mime_types():
    json_path = os.path.join(os.path.dirname(__file__), 'mime_types.json')
    with open(json_path, 'r') as f:
        return json.load(f)

# Store MIME types in a global variable
ALLOWED_MIME_TYPES = _load_mime_types()
#Base file upload URL
n_upload_url = "https://api.notion.com/v1/file_uploads"
# Error for file size exceeding 5MB    
class FileTooLargeError(Exception):
    pass

# Base class for file upload
class base_upload:
    def __init__(self, file_path, file_name, api_key, enforce_max_size=True):
        self.file_path = file_path
        self.file_name = file_name
        self.api_key = api_key
        self.enforce_max_size = enforce_max_size
        self.mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    # Validate the file before upload
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

        if self.mime_type not in ALLOWED_MIME_TYPES:
            errors.append(f"Usupported MIME type: {self.mime_type}. Please check the file type and try again.")

        if mimetypes.guess_type(self.file_name)[0] != self.mime_type:
            errors.append("Your file's file extension does not match the file type. Please check the file name and try again.")

        if errors:
            print("🛑 The following issues were found:")
            for error in errors:
                print("❌", error)
            return False
        return True
    #The first step of file upload is the same for both internal and external uploads.
    def initiate_upload(self):
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

        try:
            response = requests.post(n_upload_url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                file_id = response.json().get("id")
                print("🚀 Upload successfully started! File ID: " + file_id)
                return file_id
            else:
                print("❌ Upload failed:", response.status_code, response.text)
                return None
        except requests.RequestException as e:
            print("🌐 Upload failed due to a network error:", e)
            return None
#Internal upload
class internal_upload(base_upload):
    def __init__(self, file_path, file_name, api_key, enforce_max_size=True):
        super().__init__(file_path, file_name, api_key, enforce_max_size)
    # Upload a single file to Notion (internal)
    def singleUpload(self):
        if not self.validate():
            return None
        file_id = self.initiate_upload()
        if file_id is None:
            return None

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

                    response = requests.post(upload_url, headers=headers, files=files, timeout=10)

                    if response.status_code == 200:
                        print("✅ Upload successful! File ID: " + file_id)
                    else:
                        print("📤 Upload failed at file send stage:", response.status_code, response.text)
            except FileNotFoundError:
                print(f"📁 File not found: {self.file_path}")
        return file_id


class external_upload(base_upload):
    def __init__(self, file_path, file_name, api_key, enforce_max_size=True):
        super().__init__(file_path, file_name, api_key, enforce_max_size)
    #upload a single file to Notion (external)
    def singleUpload(self):
        """
        Upload a single file to Notion.
        """
        if not self.validate():
            return None
        file_id = self.initiate_upload()
        if file_id is None:
            return None

        # Download the file from the URL       
        file_url = self.file_path
        try:
            if self.enforce_max_size:
                head_resp = requests.head(file_url, timeout=10)
                content_length = head_resp.headers.get("Content-Length")
                if content_length and int(content_length) > 5 * 1024 * 1024:
                    raise FileTooLargeError(
                        f"File at URL '{file_url}' is {int(content_length) / (1024 * 1024):.2f}MB, which exceeds the 5MB Notion limit."
                    )
            response = requests.get(file_url, stream=True, timeout=10)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    for chunk in response.iter_content(1024):
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name

                with open(temp_file_path, "rb") as f:
                    files = {
                        "file": (self.file_name, f, self.mime_type),
                    }

                    url = f"https://api.notion.com/v1/file_uploads/{file_id}/send"
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Notion-Version": "2022-06-28"
                    }

                    response = requests.post(url, headers=headers, files=files, timeout=10)

                    print("✅ Upload successful! File ID: " + file_id)

                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            else:
                print("📥 Failed to download the file:", response.status_code)
        except requests.RequestException as e:
            print("🌐 Failed to download the file due to a network error:", e)
        return file_id


#Main class to handle file uploads
class notion_upload:
    def __init__(self, file_path, file_name, api_key, enforce_max_size=True):
        self.file_path = file_path
        self.file_name = file_name
        self.api_key = api_key
        self.enforce_max_size = enforce_max_size
        self.mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    #Logic to determine if the file is internal or external    
    def upload(self):
        if re.match(r'^(http|https)://', self.file_path):
            return external_upload(self.file_path, self.file_name, self.api_key, self.enforce_max_size).singleUpload()
        else:
            return internal_upload(self.file_path, self.file_name, self.api_key, self.enforce_max_size).singleUpload()
#This class takes a JSON object with multiple files and uploads them to Notion.
class bulk_upload:
    def __init__(self, file_json, api_key, enforce_max_size=True):
        self.file_json = file_json
        self.api_key = api_key
        self.enforce_max_size = enforce_max_size
    
    #file_json = {
    #        "files": [
    #           {"path": "file/path", "name": "name.txt"},
    #            {"path": "file/path2", "name": "name2.txt"}
    #        ]
    #   }
    #This is the format of the file_json that you need to pass to the bulk_upload class.

    def upload(self):
        file_ids = []
        try:
            files = self.file_json.get("files", [])
            if not isinstance(files, list):
                raise ValueError("Invalid format: 'files' should be a list.")
        except Exception as e:
            print("🧾 Invalid JSON structure:", e)
            return file_ids

        for file_entry in files:
            file_path = file_entry.get("path")
            file_name = file_entry.get("name")

            if not file_path or not file_name:
                print("⚠️ Skipping entry due to missing path or name:", file_entry)
                continue

            uploader = notion_upload(file_path, file_name, self.api_key, self.enforce_max_size)
            file_id = uploader.upload()
            if file_id:
                file_ids.append(file_id)
        return file_ids
