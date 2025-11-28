import requests

def test_register():
    url = "http://localhost:8000/api/auth/register"
    payload = {
        "email": "test@example.com",
        "password": "password123"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_register()
