from notion_upload.core import notion_upload
NOTION_KEY = "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"
test_upload = notion_upload(
    "test.jpg",
    "test.jpg",
    NOTION_KEY
)
test_upload.upload()