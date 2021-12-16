from tortoise import fields
from tortoise.contrib.pydantic.creator import pydantic_queryset_creator
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=64)
    password = fields.CharField(max_length=64)
    created_at = fields.DatetimeField(auto_now_add=True)

UserModel = pydantic_model_creator(User, exclude=("password",))
