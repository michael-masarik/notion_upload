import os
import pytest
from unittest.mock import patch, mock_open
from notion_upload.core import base_upload, internal_upload, external_upload, notion_upload


@pytest.fixture
def valid_api_key():
    return "secret_valid_key"


@pytest.fixture
def local_file(tmp_path):
    test_file = tmp_path / "example.txt"
    test_file.write_text("Sample content")
    return str(test_file)


@pytest.fixture
def remote_file_url():
    return "https://example.com/test.txt"


@pytest.fixture
def file_name():
    return "example.txt"


def test_base_upload_validation_passes(valid_api_key, local_file, file_name):
    uploader = base_upload(local_file, file_name, valid_api_key)
    assert uploader.validate() is True


def test_base_upload_validation_fails():
    uploader = base_upload("fakepath.txt", "", "your_notion_key")
    assert uploader.validate() is False


@patch("notion_upload.core.requests.post")
def test_internal_upload_start_post_called(mock_post, valid_api_key, local_file, file_name):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"id": "mock_file_id"}
    uploader = internal_upload(local_file, file_name, valid_api_key)

    with patch("builtins.open", mock_open(read_data="data")) as m:
        with patch("notion_upload.core.requests.post") as mock_file_post:
            mock_file_post.return_value.status_code = 200
            uploader.singleUpload()
            assert mock_file_post.called


@patch("notion_upload.core.requests.post")
@patch("notion_upload.core.requests.get")
def test_external_upload_file_download_and_send(mock_get, mock_post, valid_api_key, file_name, tmp_path):
    file_url = "https://example.com/testfile.txt"

    # Mock first POST request to get file ID
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"id": "external_mock_id"}

    # Mock the GET request to download file
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.iter_content = lambda chunk_size: [b"mock content"]

    uploader = external_upload(file_url, file_name, valid_api_key)
    uploader.singleUpload()
    assert mock_get.called
    assert mock_post.called


def test_notion_upload_chooses_internal_or_external(valid_api_key, local_file, remote_file_url, file_name):
    # Internal upload test
    internal = notion_upload(local_file, file_name, valid_api_key)
    with patch.object(internal_upload, "singleUpload") as mock_internal:
        internal.upload()
        mock_internal.assert_called_once()

    # External upload test
    external = notion_upload(remote_file_url, file_name, valid_api_key)
    with patch.object(external_upload, "singleUpload") as mock_external:
        external.upload()
        mock_external.assert_called_once()
