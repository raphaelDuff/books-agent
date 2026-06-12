from dataclasses import dataclass


@dataclass(frozen=True)
class TokenViewModel:
    access_token: str
    token_type: str
