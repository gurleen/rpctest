from typing import List
from framework.decorator import remote_proc
from framework.depends import Depends
from models import User, UserModel, generate_pass_hash
from depends import current_user

from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from warnings import simplefilter

simplefilter("ignore", BeartypeDecorHintPep585DeprecationWarning)


@remote_proc
async def get_all_users() -> List[UserModel]:
    return await UserModel.from_queryset(User.all())


@remote_proc
async def get_user_by_id(id: int) -> UserModel:
    return await UserModel.from_queryset_single(User.get(id=id))


@remote_proc
async def create_user(username: str, password: str) -> UserModel:
    new_user = await User.create_user(username=username, password=password)
    await new_user.save()
    return await UserModel.from_tortoise_orm(new_user)


@remote_proc
async def login(username: str, password: str) -> str:
    user = await User.get(username=username)
    if user.verify(password):
        return user.generate_token()


@remote_proc
async def change_password(
    new_pass: str, user: User = Depends(current_user)
) -> UserModel:
    hashed = generate_pass_hash(new_pass)
    user.password = hashed
    await user.save()
    return await UserModel.from_tortoise_orm(user)


@remote_proc
async def requires_auth(user: User = Depends(current_user)) -> str:
    return "You're logged in!"
