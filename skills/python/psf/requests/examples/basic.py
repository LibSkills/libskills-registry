import requests
from requests.exceptions import Timeout, ConnectionError, HTTPError, RequestException

# Always use a Session for multiple requests
session = requests.Session()
session.headers.update({"User-Agent": "my-app/1.0", "Accept": "application/json"})
session.timeout = (3.05, 10)  # (connect_timeout, read_timeout)

BASE_URL = "https://jsonplaceholder.typicode.com"

try:
    # GET request
    response = session.get(f"{BASE_URL}/posts/1")
    response.raise_for_status()
    post = response.json()
    print(f"Post: {post['title']}")

    # POST request with JSON body
    new_post = session.post(
        f"{BASE_URL}/posts",
        json={"title": "New Post", "body": "Content", "userId": 1},
    )
    new_post.raise_for_status()
    print(f"Created post ID: {new_post.json()['id']}")

    # Upload a file
    with open("example.txt", "w") as f:
        f.write("Hello, LibSkills!")
    with open("example.txt", "rb") as f:
        upload = session.post(
            f"{BASE_URL}/posts",
            files={"file": ("example.txt", f, "text/plain")},
            data={"title": "Upload test"},
        )
        upload.raise_for_status()

    # Stream a large response
    with session.get(f"{BASE_URL}/photos", stream=True) as r:
        r.raise_for_status()
        count = 0
        for chunk in r.iter_content(chunk_size=8192):
            count += len(chunk)
        print(f"Downloaded {count} bytes")

except Timeout:
    print("Request timed out")
except ConnectionError:
    print("Failed to connect to server")
except HTTPError as e:
    print(f"HTTP {e.response.status_code}: {e.response.text[:200]}")
except RequestException as e:
    print(f"Request failed: {e}")

finally:
    session.close()
