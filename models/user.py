from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator
from passlib.context import CryptContext
from jose import jwt


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = "DontUseInProduction!"


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=64)
    password = fields.CharField(max_length=64)
    created_at = fields.DatetimeField(auto_now_add=True)
    friends = fields.ManyToManyField("models.User")

    def verify(self, plain_pass):
        return pwd_context.verify(plain_pass, self.password)

    def generate_token(self):
        return jwt.encode({"user_id": self.id}, SECRET_KEY, algorithm="HS256")

    @staticmethod
    async def create_user(**kwargs):
        kwargs["password"] = generate_pass_hash(kwargs["password"])
        return await User.create(**kwargs)

    @staticmethod
    async def get_user_from_token(token: str) -> "User":
        decoded = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        return await User.get(id=decoded.pop("user_id"))


UserModel = pydantic_model_creator(User, exclude=("password",))


def generate_pass_hash(plain_pass: str) -> str:
    return pwd_context.hash(plain_pass)
