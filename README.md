![License](https://img.shields.io/github/license/michael-masarik/notion_upload)
![Last Commit](https://img.shields.io/github/last-commit/michael-masarik/notion_upload)
![Issues](https://img.shields.io/github/issues/michael-masarik/notion_upload)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![GitHub forks](https://img.shields.io/github/forks/michael-masarik/notion_upload?style=social)
![GitHub Repo stars](https://img.shields.io/github/stars/michael-masarik/notion_upload?style=social)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/michael-masarik/notion_upload)
[![PyPI version](https://img.shields.io/pypi/v/notion-upload.svg)](https://pypi.org/project/notion-upload/)

# notion_upload

A lightweight Python utility to upload files—both local and remote—to Notion via the [Notion API](https://developers.notion.com/). Supports internal (local) and external (URL-based) file uploads, with added support for bulk uploading multiple files at once.

## Features

* ✅ Upload local files to Notion
* 🌐 Upload files from remote URLs
* 📁 MIME type validation
* ❌ Basic error checking and reporting
* 🔒 Uses Bearer token authentication
* 📦 Optional 5MB file size enforcement (enabled by default)
* 📤 Bulk upload multiple files in a single call
* 📋 Returns Notion file IDs for uploaded files

## Installation

Clone the repo:

```bash
git clone https://github.com/michael-masarik/notion_upload.git
cd notion_upload
```

Install dependencies:

```bash
pip install -r requirements.txt
```

> The only external dependency is `requests`.

## Usage

### Single File Upload Example

```python
from notion_upload import notion_upload

NOTION_KEY = "your_notion_api_key"

#Internal
def internal_upload():
    uploader = notion_upload("internal.jpg","internal.jpg", NOTION_KEY)
    uploaded_file_ids = uploader.upload()
    print("Uploaded file IDs:", uploaded_file_ids)

internal = internal_upload()

#External
def external_upload():
    uploader = notion_upload("https://example.com/image.png","external.png", NOTION_KEY)
    uploaded_file_ids = uploader.upload()
    print("Uploaded file IDs:", uploaded_file_ids)

external = external_upload()
```

### Bulk Upload Example

```python
from notion_upload import bulk_upload

NOTION_KEY = "your_notion_api_key"

def test_bulk_upload():
    

    files_to_upload = {
        "files": [
            {
                "path": "internal.jpg",
                "name": "internal.jpg"
            },
            {
                "path": "https://example.com/image.png",
                "name": "external.png"
            }
        ]
    }

    uploader = bulk_upload(files_to_upload, NOTION_KEY)
    uploaded_file_ids = uploader.upload()
    print("Uploaded file IDs:", uploaded_file_ids)

test = test_bulk_upload()
```

## File Types

Supported file types depend on the Notion API. Common formats like PDFs, images, and documents should work. Python’s built-in `mimetypes` module is used to infer MIME types.

## Validation

* Ensures a Notion API key is provided
* Validates that the file extension matches the inferred MIME type
* Optionally enforces Notion's 5MB upload limit (can be disabled)
* Prints clear, user-friendly errors on failure

## Notes

* For external uploads, the file is downloaded temporarily and deleted after the upload
* Make sure your Notion integration has appropriate permissions for file uploads
* By default, files larger than 5MB will raise an error. To override this, pass `enforce_max_size=False`.
* Bulk uploads return a list of Notion file IDs corresponding to each uploaded file.

## License

MIT License

## Contributing

Contributions are welcome! Feel free to fork the repo, submit pull requests, or open issues. See version notes below.

## Version Notes

Currently, `notion_upload` supports single-part uploads and bulk upload of multiple files due to limitations of the free [Notion plan](https://www.notion.com/pricing). If you have access to a Business or Enterprise plan, feel free to contribute to the multi-part file upload!
