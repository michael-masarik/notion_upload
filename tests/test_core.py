from notion_upload.core import notion_upload
NOTION_KEY = "***"
test_upload = notion_upload(
    "test.jpg",
    "test.jpg",
    NOTION_KEY
)
test_upload.upload()
