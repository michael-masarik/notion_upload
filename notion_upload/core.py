import os
import re
from typing import BinaryIO

import requests
import mimetypes

ALLOWED_MIME_TYPES = {}  # TODO


class FileToLarge(Exception):
    pass


class InvaildMIME(Exception):
    pass


class MultiPartUpload:
    api_key: str

    def __init__(self, api_key) -> None:
        self.api_key = api_key

    def split(self, file: BinaryIO):
        while True:
            chunk = file.read(10 * 1024 * 1024)
            if not chunk:
                break
            yield chunk

    def upload(self, filepath):  # TODO: Implement this!!
        with open(filepath, "rb") as file:
            for chunk in self.split(file):
                pass


class notionUpload:
    NOTION_URL = "https://api.notion.com/v1/file_uploads"

    def __init__(
        self,
        file_path: str,
        file_name: str,
        api_key: str,
        enforce_max_size=True,
    ):

        self.filePath = file_path
        self.fileName = file_name
        self.mimeType = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        self.apiKey = api_key
        self.bulkUpload = MultiPartUpload(self.apiKey)
        if enforce_max_size:
            self.maxBytes = 5242880
        else:
            self.maxBytes = 5368709120
        if re.match(r"^(http|https)://", self.filePath):
            self.type = "external"
        else:
            self.type = "internal"
            if os.path.isfile(self.filePath):
                fileSize = os.path.getsize(self.filePath)
                if fileSize > self.maxBytes:
                    raise FileToLarge(
                        f"File '{self.filePath}' is {fileSize / (1024 * 1024):.2f}MB, which exceeds the {self.maxBytes / (1024 * 1024):.2f}MB limit imposed by Notion"
                    )
                elif fileSize >= 2e7:
                    self.multiPart = True
            else:
                raise FileNotFoundError(self.filePath)
        if self.mimeType not in ALLOWED_MIME_TYPES:
            raise InvaildMIME(f"{self.mimeType} is not a support MIME type")
        if mimetypes.guess_type(self.fileName)[0] != self.mimeType:
            raise InvaildMIME("File extension and MIME type do not match")

    def initiate_upload(self, external=False):
        payload = {"filename": self.fileName, "content_type": self.mimeType}
        if external:
            payload["mode"] = "external_url"
            payload["external_url"] = self.filePath
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.apiKey}",
            "Notion-Version": "2025-09-03",
        }

        try:
            response = requests.post(
                url=self.NOTION_URL, json=payload, headers=headers, timeout=10
            )
            if response.status_code == 200:
                file_id = response.json().get("id")
                if external == False:
                    print("🚀 Upload successfully started! File ID: " + file_id)
                else:
                    print("✅ Upload successful! File ID: " + file_id)
                return file_id
            else:
                print("❌ Upload failed:", response.status_code, response.text)
                return None
        except requests.RequestException as e:
            print("🌐 Upload failed due to a network error:", e)
            return None

    def singleUpload(self):
        file_id = self.initiate_upload()
        if file_id is None:
            return None

        try:
            with open(self.filePath, "rb") as f:
                files = {"file": (self.fileName, f, self.mimeType)}

                upload_url = f"https://api.notion.com/v1/file_uploads/{file_id}/send"
                headers = {
                    "Authorization": f"Bearer {self.apiKey}",
                    "Notion-Version": "2022-06-28",
                }

                response = requests.post(
                    upload_url, headers=headers, files=files, timeout=10
                )

                if response.status_code == 200:
                    print("✅ Upload successful! File ID: " + file_id)
                else:
                    print(
                        "📤 Upload failed at file send stage:",
                        response.status_code,
                        response.text,
                    )
        except FileNotFoundError:
            print(f"📁 File not found: {self.filePath}")
        return file_id

    def upload(self):
        pass


# Type alias
notion_upload = notionUpload
