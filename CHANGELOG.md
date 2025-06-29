# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
## [1.3.2] - 2025-05-21
## Changed 
- Corrected file bug. MIME types file was not included in the build.
## [1.3.1] - 2025-05-21
### Changed 
- Improved logging
### Added
- Support Checking for MIME types. To view supported MIME types, [click here](notion_upload/mime_types.json)
## [1.2.1] - 2025-05-19
### Changed
- Changed typo in README.md
## [1.2.0] - 2025-05-19

### Added
- By importing `bulk_upload`, you can import many files via JSON (the ids will be returned via a [])

## [1.1.0] - 2025-05-19

### Added
- Optional file size enforcement for uploads (enabled by default, max 5MB).
- New `enforce_max_size` parameter for `notion_upload`, `internal_upload`, and `external_upload`.
- Custom `FileTooLargeError` raised if file exceeds limit.
- Remote file size is checked via `Content-Length` header before download when available.

### Changed
- External uploads now perform a HEAD request before download (if size check is enabled).

### Notes
- The default 5MB file limit reflects Notion's current upload limit.
- You can disable this check by passing `enforce_max_size=False`.


## [1.0.2] - 2025-05-17

### Added
* Added test files

### Notes
* Multi-part upload is not included in this release due to Notion's free plan limitations.



## [1.0.1] - 2025-05-16

### Added
* Minor changes to meta-data

### Notes
* Multi-part upload is not included in this release due to Notion's free plan limitations.

## [1.0.0] - 2025-05-16

### Added

* Initial stable release of `notion_upload`.
* Upload support for local files.
* Upload support for remote files via URL.
* MIME type detection using Python’s built-in `mimetypes`.
* Basic error handling and validation.
* Temporary file handling for external uploads.

### Notes

* Multi-part upload is not included in this release due to Notion's free plan limitations.
