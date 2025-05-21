# Shared imports for all tests
from src.user.models.user import User
from src.user.models.user_photo import UserPhoto
from src.match.models.userLiked import UserLiked
from src.messages.models.message import Message
from src.hobby.models.hobby import Hobby
from src.hobby.models.category import Category

__all__ = ["User", "UserPhoto", "UserLiked", "Message", "Hobby", "Category"]