import requests
from abc import ABC, abstractmethod

class Browser(ABC):

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })

    @abstractmethod
    def login(self, username, password):
        pass

    @abstractmethod
    def get_schedule(self):
        pass