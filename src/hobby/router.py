from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.dependencies import get_token_data
from src.hobby.service import HobbyService
from src.hobby.schemas.hobby import HobbySchema
from src.database import get_db
from src.auth.utils.util import AuthUtil
from src.auth.schemas.token_data import TokenData

router = APIRouter(
    prefix="/hobby",
    tags=["hobby"]
)


@router.get("/user", response_model=list[HobbySchema])
async def get_user_hobbies(token: TokenData = Depends(get_token_data), db: AsyncSession = Depends(get_db)):
    """
    Endpoint to get hobbies for the authenticated user.
    """
    service = HobbyService(db)
    return await service.get_user_hobbies(token.id)


@router.post("/user", response_model=dict)
async def add_user_hobbies(hobby_ids: list[int], token: TokenData = Depends(get_token_data), db: AsyncSession = Depends(get_db)):
    """
    Endpoint to add multiple hobbies for the authenticated user.
    """
    service = HobbyService(db)
    return await service.add_user_hobbies(token.id, hobby_ids)


@router.put("/user", response_model=dict)
async def edit_user_hobbies(hobby_ids: list[int],  token: TokenData = Depends(get_token_data), db: AsyncSession = Depends(get_db)):
    """
    Endpoint to edit a hobby for the authenticated user.
    """
    service = HobbyService(db)
    return await service.edit_user_hobbies(token.id, hobby_ids)


@router.delete("/user", response_model=dict)
async def delete_user_hobbies(hobby_ids: list[int], token: TokenData = Depends(get_token_data), db: AsyncSession = Depends(get_db)):
    """
    Endpoint to delete multiple hobbies for the authenticated user.
    """
    service = HobbyService(db)
    return await service.delete_user_hobbies(token.id, hobby_ids)

@router.get("/search", response_model=list[HobbySchema])
async def search_hobbies(query: str, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to search hobbies by name or category.
    """
    service = HobbyService(db)
    return await service.search_hobbies(query)


@router.get("/{hobby_id}", response_model=HobbySchema)
async def get_hobby(hobby_id: int, db: AsyncSession = Depends(get_db)):
    service = HobbyService(db)
    return await service.get_hobby(hobby_id)

@router.post("/", response_model=HobbySchema)
async def create_hobby(hobby_data: HobbySchema, db: AsyncSession = Depends(get_db)):
    service = HobbyService(db)
    return await service.create_hobby(hobby_data)


@router.put("/{hobby_id}", response_model=HobbySchema)
async def update_hobby(hobby_id: int, hobby_data: HobbySchema, db: AsyncSession = Depends(get_db)):
    service = HobbyService(db)
    return await service.update_hobby(hobby_id, hobby_data)


@router.delete("/{hobby_id}")
async def delete_hobby(hobby_id: int, db: AsyncSession = Depends(get_db)):
    service = HobbyService(db)
    return await service.delete_hobby(hobby_id)
