import requests

response = requests.post("http://localhost:1234/api/led", json={"state": "off"})
