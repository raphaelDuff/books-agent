from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    # TODO: Use this interface from application use cases for easier unit testing.

    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        raise NotImplementedError
