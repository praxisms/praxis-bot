import requests


class DiscordWebhook:
    def __init__(self, url: str):
        self.__url = url

    def send(self, markdown):
        requests.post(self.__url, json={
            "content": markdown
        })
