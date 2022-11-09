import requests


class API:

    def __init__(self):
        self.host = 'https://api.opendota.com/api/'

    def get_match_info(self, match_id: str) -> dict:
        result = requests.get(url=self.host + f'/matches/{match_id}').json()
        return result


