import os
import re
from typing import BinaryIO

import requests


class FileToLarge(Exception):
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

    def __init__(
        self,
        file_path: str,
        file_name: str,
        api_key: str,
        enforce_max_size=True,
    ):
        self.filePath = file_path
        self.fileName = file_name
        self.apiKey = api_key
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

        # self.mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'


# Type alias
notion_upload = notionUpload
