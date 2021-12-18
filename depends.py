from framework.context_vars import auth_token
from models import User


async def current_user() -> User:
    token = auth_token.get()
    return await User.get_user_from_token(token)
