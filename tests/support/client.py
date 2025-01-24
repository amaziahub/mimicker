import requests


class Client:

    def __init__(self, root='http://localhost:8080'):
        self.root = root

    def get(self, path, headers=None, **kwargs):
        return requests.get(f"{self.root + path}", headers=headers, **kwargs)

    def post_as_json(self, path, body=None, headers=None):
        return requests.post(f"{self.root + path}", json=body, headers=headers)

    def post_as_text(self, path, body=None, headers=None):
        headers = headers or {}
        headers['Content-Type'] = 'text/plain'
        return requests.post(f"{self.root + path}", data=body, headers=headers)

    def post_as_image(self, path, body=None, headers=None):
        headers = headers or {}
        headers['Content-Type'] = 'image/png'
        return requests.post(f"{self.root + path}", data=body, headers=headers)

    def post_as_file(self, path, body=None, headers=None):
        return requests.post(f"{self.root + path}", files=body, headers=headers)

    def put_as_json(self, path, body=None, headers=None):
        return requests.put(f"{self.root + path}", json=body, headers=headers)

    def put_as_text(self, path, body=None, headers=None):
        return requests.put(f"{self.root + path}", data=body, headers=headers)

    def put_as_file(self, path, body=None, headers=None):
        return requests.put(f"{self.root + path}", files=body, headers=headers)

    def put(self, path, body=None, headers=None):
        return requests.put(f"{self.root + path}", json=body, headers=headers)

    def delete(self, path, headers=None):
        return requests.delete(f"{self.root + path}", headers=headers)
