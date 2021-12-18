import asyncio
import re
import orjson
from datetime import datetime
from loguru import logger
from tortoise import Tortoise, run_async
from tortoise.contrib.pydantic.base import PydanticListModel, PydanticModel
from framework.depends import resolve_dependencies
from models import User
from framework.decorator import rpc_functions
from operator import itemgetter as get
from typing import Any, Callable, Mapping
from beartype.roar import BeartypeException
from .context_vars import auth_token


def result_json(result: Any) -> Mapping:
    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], PydanticModel):
            return [r.dict() for r in result]
    elif isinstance(result, PydanticListModel) or isinstance(result, PydanticModel):
        return result.dict()
    return result


async def handle_request(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    data: bytes = await reader.readuntil(b"\r\n")
    message = orjson.loads(data.strip().decode("utf-8"))

    function, args = get("function", "args")(message)
    token = message.get("token")
    auth_token.set(token)
    logger.info(f"{function} called with {args}")

    handler: Callable = rpc_functions.get(function)

    args = await resolve_dependencies(handler, args)

    if handler is not None:
        try:
            value = await handler(*args)
            value_json = result_json(value)
            return_value = {
                "success": True,
                "time": datetime.now(),
                "value": value_json,
            }
        except BeartypeException as e:
            return_value = {"success": False, "error": str(e)}
        except TypeError as e:
            return_value = {"success": False, "error": "There was a type mismatch."}
        """
        except:
            return_value = {
                "success": False,
                "error": "Still trying to figure it out!"
            }
        """

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
    server = await asyncio.start_server(handle_request, "127.0.0.1", 5000)
    async with server:
        logger.info("Server started.")
        await server.serve_forever()


if __name__ == "__main__":
    run_async(main())
