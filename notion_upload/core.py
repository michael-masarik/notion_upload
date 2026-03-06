from math import ceil
import os
import re
from typing import BinaryIO
from mime_types import NOTION_MIME_TYPES as ALLOWED_MIME_TYPES
import time

import requests
import mimetypes

CHUNK_SIZE = 10 * 1024 * 1024
NOTION_URL = "https://api.notion.com/v1/file_uploads"
TIME_FREQUENCY = 3
PERIOD = 1.0 / TIME_FREQUENCY


class FileToLarge(Exception):
    pass


class InvaildMIME(Exception):
    pass


class MultiPartUpload:
    api_key: str

    def __init__(self, api_key: str, filePath: str, fileName: str, mimeType: str):
        self.api_key = api_key
        self.filePath = filePath
        self.fileName = fileName
        self.mimeType = mimeType
        self.current = 0
        if os.path.isfile(filePath):
            fileSize = os.path.getsize(filePath)
            self.chunkCount = ceil(fileSize / CHUNK_SIZE)

    def split(self, file: BinaryIO):
        while True:
            chunk = file.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk

    def initiate_upload(self):
        payload = {
            "filename": self.fileName,
            "content_type": self.mimeType,
            "mode": "multi_part",
            "number_of_parts": self.chunkCount,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2025-09-03",
        }

        try:
            response = requests.post(
                url=NOTION_URL, json=payload, headers=headers, timeout=10
            )
            if response.status_code == 200:
                file_id = response.json().get("id")
                print("✅ Upload Started! File ID: " + file_id)
                return file_id
            else:
                print("❌ Upload failed:", response.status_code, response.text)
                return None
        except requests.RequestException as e:
            print("🌐 Upload failed due to a network error:", e)
            return None

    def upload(self):
        file_id = self.initiate_upload()
        if file_id == None:
            return None
        with open(self.filePath, "rb") as file:
            for chunk in self.split(file):
                start_time = time.time()
                try:
                    self.current += 1
                    files = {
                        "file": (self.fileName, chunk, self.mimeType),
                    }

                    upload_url = (
                        f"https://api.notion.com/v1/file_uploads/{file_id}/send"
                    )
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Notion-Version": "2025-09-03",
                    }
                    print("📡 Uploading part", self.current)
                    response = requests.post(
                        upload_url,
                        headers=headers,
                        files=files,
                        data={"part_number": self.current},
                    )
                    if response.status_code != 200:
                        print("❌ Upload failed:", response.status_code, response.text)
                        print("Chunks uploaded:", self.current - 1)
                        print("Chunks Total:", self.chunkCount)
                        break
                except requests.RequestException as e:
                    print("🌐 Upload failed due to a network error:", e)
                    break

                elapsed_time = time.time() - start_time
                sleep_time = PERIOD - elapsed_time
                if sleep_time > 0:
                    time.sleep(sleep_time)
                print(f" Actual iteration time: {time.time() - start_time:.4f} seconds")
            else:
                print("🚀 Upload successfull File ID: " + file_id)
                return file_id
        return None


class notion_upload:

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
        self.multiPart = False
        self.multiUpload = MultiPartUpload(
            self.apiKey, self.filePath, self.fileName, self.mimeType
        )
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
        if self.mimeType not in ALLOWED_MIME_TYPES and self.type == "internal":
            raise InvaildMIME(f"{self.mimeType} is not a support MIME type")
        if (
            mimetypes.guess_type(self.fileName)[0] != self.mimeType
        ) and self.type == "internal":
            raise InvaildMIME("File Name extension and MIME type do not match")

    def initiate_upload(self, external=False):
        payload = {"filename": self.fileName, "content_type": self.mimeType}
        if external:
            payload["mode"] = "external_url"
            payload["external_url"] = self.filePath
            del payload["content_type"]
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.apiKey}",
            "Notion-Version": "2025-09-03",
        }

        try:
            response = requests.post(url=NOTION_URL, json=payload, headers=headers)
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
                    "Notion-Version": "2025-09-03",
                }

                response = requests.post(upload_url, headers=headers, files=files)

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
        if self.type == "external":
            return self.initiate_upload(external=True)
        elif self.multiPart == True:
            return self.multiUpload.upload()
        else:
            return self.singleUpload()


class bulk_upload:
    def __init__(self, files: dict, api_key, enforce_max_size=True):
        self.files = files.get("files", [])
        try:
            if not isinstance(self.files, list):
                raise ValueError("Invalid format: 'files' should be a list.")
        except Exception as e:
            print("🧾 Invalid JSON structure:", e)
        self.apiKey = api_key
        self.MaxSize = enforce_max_size

    def upload(self):
        file_ids = []
        for file_entry in self.files:
            file_path = file_entry.get("path")
            file_name = file_entry.get("name")
            if not file_path or not file_name:
                print("⚠️ Skipping entry due to missing path or name:", file_entry)
                continue
            uploader = notion_upload(
                file_path, file_name, self.apiKey, enforce_max_size=self.MaxSize
            )
            fileID = uploader.upload()
            if fileID:
                file_ids.append(fileID)
        return file_ids

    def upload_generator(self):
        for file_entry in self.files:
            file_path = file_entry.get("path")
            file_name = file_entry.get("name")
            if not file_path or not file_name:
                print("⚠️ Skipping entry due to missing path or name:", file_entry)
                continue
            uploader = notion_upload(
                file_path, file_name, self.apiKey, enforce_max_size=self.MaxSize
            )
            yield uploader.upload()
