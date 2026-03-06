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
Install the package
```bash
pip install notion-upload
```
> The only external dependency is `requests`.

## Usage

### Single File Upload Example

```python
from notion_upload import notion_upload

NOTION_KEY = "your_notion_api_key"

#Internal
 uploader = notion_upload(
    "internal.jpg",
    "internal.jpg", 
    NOTION_KEY
 )
uploaded_file_id = uploader.upload()
print("Uploaded file ID:", uploaded_file_id)


#External
uploader = notion_upload(
    "https://example.com/image.png","external.png", 
    NOTION_KEY
)
uploaded_file_ids = uploader.upload()
print("Uploaded file IDs:", uploaded_file_ids)
```

### Bulk Upload Example

```python
from notion_upload import bulk_upload

NOTION_KEY = "your_notion_api_key"

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

# If you would prefer a generator over a returned list, use upload_generator()
uploader.upload_generator()
print("Uploaded file IDs:", uploaded_file_ids)
```

## File Types

Supported file types depend on the Notion API. Common formats like PDFs, images, and documents should work. Python’s built-in `mimetypes` module is used to infer MIME types. To see which file types are allowed, view the `mime_types.py` file. 

## Validation

* Ensures a Notion API key is provided
* Validates that the file extension matches the inferred MIME type
* Validates that the MIME type is the supported in Notion
* Optionally enforces Notion's 5MB upload limit (can be disabled)
* Prints clear, user-friendly errors on failure
* Throws clear errors on validation issues before attempting to upload

## Notes

* Make sure your Notion integration has appropriate permissions for file uploads
* By default, files larger than 5MB will raise an error. To override this, pass `enforce_max_size=False`.
* `enforce_max_size=False` does not prevent uploads from failing on files bigger than 5GB (Notion's hard ceiling for file size).
* Bulk uploads return a list of Notion file IDs corresponding to each uploaded file.

## License

MIT License

## Contributing

Contributions are welcome! Feel free to fork the repo, submit pull requests, or open issues.

