from collections import UserList
import functools
from typing import List
from models import User, UserModel
from beartype import beartype


rpc_functions = {}

def remote_proc(func):
    rpc_functions[func.__name__] = func
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        value = func(*args, **kwargs)
        return value
    return wrapper_decorator


@remote_proc
async def get_all_users() -> List[UserModel]:
    return await UserModel.from_queryset(User.all())


@remote_proc
@beartype
async def get_user_by_id(id: int) -> UserModel:
    return await UserModel.from_queryset_single(User.get(id=id))

@remote_proc
@beartype
async def create_user(username: str, password: str) -> UserModel:
    new_user = await User.create_user(username=username, password=password)
    await new_user.save()
    return await UserModel.from_tortoise_orm(new_user)


@remote_proc
@beartype
async def login(username: str, password: str) -> bool:
    user = await User.get(username=username)
    return user.verify(password)


@remote_proc
async def add(a: int, b: int) -> int:
    return a + b