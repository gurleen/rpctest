import asyncio
import orjson
import inspect
from datetime import datetime
from loguru import logger
from tortoise import Tortoise, run_async
from tortoise.contrib.pydantic.base import PydanticListModel, PydanticModel
from models import User
from rpc import rpc_functions
from operator import itemgetter as get
from typing import Any, Callable
from beartype.roar import BeartypeException


def result_json(result: Any) -> str:
    if isinstance(result, list) and isinstance(result[0], PydanticModel):
        return [r.dict() for r in result]
    elif isinstance(result, PydanticListModel) or isinstance(result, PydanticModel):
        return result.dict()
    return result


def requires_user(func: Callable) -> bool:
    sig = inspect.signature(func)
    if list(sig.parameters)[0] == "user":
        return sig.parameters["user"].annotation == User
    return False


async def handle_request(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    data: bytes = await reader.readuntil(b"\r\n")
    message = orjson.loads(data.strip().decode("utf-8"))
    no_error = True

    function, args = get("function", "args")(message)
    token = message.get("token")
    logger.info(f"{function} called with {args}")

    handler = rpc_functions.get(function)
    handler_requires_user = requires_user(handler)

    if handler_requires_user:
        if token is None:
            return_value = {
                "success": False,
                "error": "Authorization required."
            }
            no_error = False
        else:
            user = await User.get_user_from_token(token)
            args = (user, *args)
    
    if handler is not None and no_error:
        try:
            value = await handler(*args)
            value_json = result_json(value)
            return_value = {
                "success": True,
                "time": datetime.now(),
                "value": value_json
            }
        except BeartypeException as e:
            return_value = {
                "success": False,
                "error": str(e)
            }
        except TypeError as e:
            return_value = {
                "success": False,
                "error": "There was a type mismatch."
            }
        except:
            return_value = {
                "success": False,
                "error": "Still trying to figure it out!"
            }
    
    writer.write(orjson.dumps(return_value) + b"\r\n")
    await writer.drain()

    writer.close()


async def main():
    logger.info("Starting RPC server...")
    logger.info("Initializing Tortoise")
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["models"]})
    logger.info("Generating schemas")
    await Tortoise.generate_schemas()

    user = await User.create_user(username="gurleen", password="password")
    await user.save()

    user2 = await User.create_user(username="trey", password="password2")
    await user2.save()

    logger.info("Starting async event loop")
    server = await asyncio.start_server(handle_request, '127.0.0.1', 5000)
    async with server:
        logger.info("Server started.")
        await server.serve_forever()


run_async(main())