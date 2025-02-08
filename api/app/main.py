from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
import requests
import os
import logging

app = FastAPI()
security = HTTPBearer()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
REALM = os.getenv("KEYCLOAK_REALM", "reports-realm")
CLIENT_IDS = ["reports-api", "reports-frontend"]
ISSUERS = [
    f"http://localhost:8080/realms/{REALM}",
    f"{KEYCLOAK_URL}/realms/{REALM}"
]
WELL_KNOWN_URL = f"{KEYCLOAK_URL}/realms/{REALM}/.well-known/openid-configuration"

def get_jwks():
    try:
        res = requests.get(WELL_KNOWN_URL)
        res.raise_for_status()
        jwks_uri = res.json()["jwks_uri"]
        jwks_data = requests.get(jwks_uri).json()
        return jwks_data
    except Exception as e:
        logging.info(f"JWKS fetch error: {e}")
        return None

def decode_token(token: str):
    jwks = get_jwks()
    if not jwks:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWKS fetch failed")

    unverified_header = jwt.get_unverified_header(token)
    logging.info(f"Unverified Header: {unverified_header}")
    kid = unverified_header.get("kid")

    key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if not key:
        logging.info(f"Key with kid={kid} not found in JWKS")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    logging.info(f"Using key: {key}")

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"]
        )
        logging.info(f"Token payload: {payload}")

        audience = payload.get("aud")
        if audience:
            if isinstance(audience, list):
                if not any(aud in CLIENT_IDS for aud in audience):
                    logging.error(f"Invalid audience: {audience}")
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid audience")
            else:
                if audience not in CLIENT_IDS:
                    logging.error(f"Invalid audience: {audience}")
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid audience")
        else:
            logging.info("No audience field in token, skipping audience check.")

        if payload.get("iss") not in ISSUERS:
            logging.error(f"Invalid issuer: {payload.get('iss')}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid issuer")

        return payload
    except JWTError as e:
        logging.error(f"Token validation error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token validation failed")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return decode_token(token)


@app.get("/reports")
def get_reports(user: dict = Depends(get_current_user)):
    roles = user.get("realm_access", {}).get("roles", [])
    if "prothetic_user" not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

    return {
        "reportData": [
            {"id": 1, "value": "Report item 1"},
            {"id": 2, "value": "Report item 2"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
