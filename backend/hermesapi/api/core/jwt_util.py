from jose import jwt
import datetime


class JWTUtil:
    def __init__(self, secret, algorithm, timeout):
        self.secret = secret
        self.algorithm = algorithm
        self.timeout = timeout

    def encode_token(self, user):
        payload = {
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(seconds=self.timeout),
            "iat": datetime.datetime.utcnow(),
            "scope": "access_token",
            "sub": str(user.id),
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            if payload["scope"] == "access_token":
                return payload["sub"]
            raise HTTPException(
                status_code=401, detail="Scope for the token is invalid"
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def encode_refresh_token(self, user):
        payload = {
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(seconds=self.timeout),
            "iat": datetime.datetime.utcnow(),
            "scope": "refresh_token",
            "sub": str(user.id),
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def refresh_token(self, refresh_token):
        try:
            payload = jwt.decode(
                refresh_token, self.secret, algorithms=[self.algorithm]
            )
            if payload["scope"] == "refresh_token":
                username = payload["sub"]
                new_token = self.encode_token(username)
                return new_token
            raise HTTPException(status_code=401, detail="Invalid scope for token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
