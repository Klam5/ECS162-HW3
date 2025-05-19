# https://docs.pytest.org/en/stable/

import os
from app import app

# first test ensures backend works correctly in terms of pulling articles by checking the existence of docs in response and that it is a list which will be outputted as article data
def test():
    assert os.getenv("NYT_API_KEY") is not None, "API key not fetched"
    test_client = app.test_client()
    response = test_client.get("/api/news")
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'response' in json_data, "response not returned"
    assert 'docs' in json_data['response'], "docs not in response"
    assert isinstance(json_data["response"]["docs"], list), "docs != in list"

# this test makes sure that the api key is the same as the one in .env file, using the correct key
# mainly decided to implement this for sanity check
def test_returns_api_key():
    test_client = app.test_client()
    response = test_client.get("/api/key")
    data = response.get_json()
    assert "key" in data
    assert data["key"] == os.getenv("NYT_API_KEY")

# this test checks /api/news and ensures that the articles being pulled and displayed contain "davis" or "sacramento" in their location tags
# makes sure we are pulling davis and/or sacramento articles
def test_from_davis_sac():
    test_client = app.test_client()
    response = test_client.get("/api/news")
    assert response.status_code == 200

    json_data = response.get_json()
    assert 'response' in json_data
    assert 'docs' in json_data['response']
    articles = json_data['response']['docs']
    assert len(articles) > 0, "No articles returned"

    for article in articles:
        keywords = article.get("keywords", [])
        location = [k["value"].lower() for k in keywords if k.get("name") == "Location"]
        correctCity = any("davis" in loc or "sacramento" in loc for loc in location)
        assert correctCity, f"Article missing required location tags: {location}"