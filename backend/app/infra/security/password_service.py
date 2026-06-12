from pwdlib import PasswordHash

from app.application.service_ports.password_hasher import PasswordHasher


class PasswordService(PasswordHasher):

    password_hash = PasswordHash.recommended()
    DUMMY_HASH = password_hash.hash("dummyverydummypassword")

    def hash_password(self, plain_password: str) -> str:
        return self.password_hash.hash(plain_password)

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        return self.password_hash.verify(plain_password, password_hash)
