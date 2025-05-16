# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## \[1.0.0] - 2025-05-16

### Added

* Initial stable release of `notion_upload`.
* Upload support for local files.
* Upload support for remote files via URL.
* MIME type detection using Python’s built-in `mimetypes`.
* Basic error handling and validation.
* Temporary file handling for external uploads.

### Notes

* Multi-part upload is not included in this release due to Notion's free plan limitations.
