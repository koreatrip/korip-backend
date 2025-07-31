from abc import ABC, abstractmethod

class OAuthProvider(ABC):
    @abstractmethod
    def get_token(self, code: str) -> str:
        pass

    @abstractmethod
    def get_user_info(self, access_token: str) -> dict:
        pass