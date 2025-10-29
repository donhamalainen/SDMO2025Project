import json
from unittest.mock import patch, mock_open
from lmstudio_connector import send_devs_and_get_similarity

MOCK_JSON_RESPONSE = {
    "choices": [
        {
            "message": {
                "content": json.dumps([{"name": "John Doe", "matched_with": "Jon Doe"}])
            }
        }
    ]
}

@patch("builtins.open", new_callable=mock_open, read_data="name,email\nJohn Doe,john@example.com\nJon Doe,jon@example.com\n")
@patch("lmstudio_connector.requests.post")
def test_send_devs_and_get_similarity(mock_post, mock_file):
    mock_post.return_value.json.return_value = MOCK_JSON_RESPONSE
    mock_post.return_value.raise_for_status = lambda: None

    result = send_devs_and_get_similarity("fake_path.csv")
    assert isinstance(result, list)
    assert result[0]["name"] == "John Doe"
    mock_post.assert_called_once()