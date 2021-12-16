from tortoise import fields
from tortoise.contrib.pydantic.creator import pydantic_queryset_creator
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=64)
    password = fields.CharField(max_length=64)
    created_at = fields.DatetimeField(auto_now_add=True)

    def verify(self, plain_pass):
        return pwd_context.verify(plain_pass, self.password)

    @staticmethod
    async def create_user(**kwargs):
        kwargs["password"] = generate_pass_hash(kwargs["password"])
        return await User.create(**kwargs)

UserModel = pydantic_model_creator(User, exclude=("password",))


def generate_pass_hash(plain_pass: str) -> str:
    return pwd_context.hash(plain_pass)