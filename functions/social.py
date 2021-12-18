from typing import List
from framework import remote_proc, Depends
from models import User
from depends import current_user
from models.user import UserModel


@remote_proc
async def add_friend(user_id: int, user: User = Depends(current_user)):
    friend = await User.get(id=user_id)
    await user.friends.add(friend)


@remote_proc
async def get_friends(user: User = Depends(current_user)) -> List[UserModel]:
    return await UserModel.from_queryset(user.friends.all())


@remote_proc
async def remove_friend(user_id: int, user: User = Depends(current_user)):
    friend = await User.get(id=user_id)
    await user.friends.remove(friend)