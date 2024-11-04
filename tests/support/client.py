import requests


class Client:

    def __init__(self, root='http://localhost:8080'):
        self.root = root

    def get(self, path):
        return requests.get(f"{self.root + path}")
