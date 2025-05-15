from fastapi import Depends, HTTPException, Header
from src.auth.utils.util import AuthUtil
from src.auth.schemas.token_data import TokenData
from src.auth.schemas.token import TokenSchema
from typing import Optional


async def get_token_data(token: TokenSchema = Header(..., alias="Authorization")) -> TokenData:
    if not token.access_token:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    try:
        token_data = AuthUtil.TokenVerification(token.access_token)
        return token_data
    except HTTPException as e:
        raise e
