from fastapi import APIRouter, Depends, HTTPException, status, Response, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.hobby.schemas.category import CategorySchema, CategoryCreate
from src.database import get_db
from src.hobby.schemas.hobby import HobbySchema, HobbyCreate, HobbyUpdate
from src.hobby.service import HobbyService
from src.auth.schemas.token_data import TokenData
from src.auth.dependencies import get_token_data

router = APIRouter(
    prefix="/hobbies",
    tags=["hobbies"]
)


@router.post("/", response_model=HobbySchema, status_code=status.HTTP_201_CREATED)
async def create_new_hobby(
    hobby_data: HobbyCreate,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    service = HobbyService(db)
    return await service.create_hobby(hobby_data=hobby_data)


@router.get("/{hobby_id}", response_model=HobbySchema)
async def get_hobby_by_id(
    hobby_id: int,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    service = HobbyService(db)
    hobby = await service.get_hobby(hobby_id=hobby_id)
    if not hobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")
    return hobby


@router.put("/{hobby_id}", response_model=HobbySchema)
async def update_existing_hobby(
    hobby_id: int,
    hobby_data: HobbyUpdate,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    service = HobbyService(db)
    return await service.update_hobby(hobby_id=hobby_id, hobby_data=hobby_data)


@router.delete("/{hobby_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_hobby(
    hobby_id: int,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    service = HobbyService(db)
    await service.delete_hobby(hobby_id=hobby_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/", response_model=List[HobbySchema])
async def search_all_hobbies(
    query: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    service = HobbyService(db)
    if query:  # Simplified logic, assuming search_hobbies is the primary way to list/filter
        return await service.search_hobbies(query=query)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Query parameter is required for searching hobbies, or provide a general listing endpoint.")


@router.get("/my/", response_model=List[HobbySchema])
async def get_my_hobbies(
    token: TokenData = Depends(get_token_data),
    db: AsyncSession = Depends(get_db)
):
    service = HobbyService(db)
    return await service.get_user_hobbies(user_id=token.id)


@router.post("/my/", response_model=dict)  # Or a more specific response schema
async def add_hobbies_to_my_profile(
    hobby_ids: List[int],  # Expect a list of hobby IDs in the request body
    token: TokenData = Depends(get_token_data),
    db: AsyncSession = Depends(get_db)
):
    service = HobbyService(db)
    return await service.add_user_hobbies(user_id=token.id, hobby_ids=hobby_ids)


@router.put("/my/", response_model=dict)  # Or a more specific response schema
async def edit_my_hobbies_on_profile(
    hobby_ids: List[int],  # Expect a list of hobby IDs in the request body
    token: TokenData = Depends(get_token_data),
    db: AsyncSession = Depends(get_db)
):
    service = HobbyService(db)
    return await service.edit_user_hobbies(user_id=token.id, hobby_ids=hobby_ids)


@router.delete("/my/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hobbies_from_my_profile(
    hobby_ids: List[int],  # Expect a list of hobby IDs in the request body
    token: TokenData = Depends(get_token_data),
    db: AsyncSession = Depends(get_db)
):
    service = HobbyService(db)
    await service.delete_user_hobbies(user_id=token.id, hobby_ids=hobby_ids)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/categories/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_new_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    service = HobbyService(db)
    return await service.create_category(name=category.name)


@router.get("/categories/", response_model=List[CategorySchema])
async def get_all_categories(
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    service = HobbyService(db)
    return await service.get_all_categories()


@router.get("/categories/{category_id}", response_model=CategorySchema)
async def get_category_by_id(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    service = HobbyService(db)
    return await service.get_category(category_id=category_id)


@router.put("/categories/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    service = HobbyService(db)
    return await service.update_category(category_id=category_id, name=category.name)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    service = HobbyService(db)
    await service.delete_category(category_id=category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
