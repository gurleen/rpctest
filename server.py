import asyncio
import orjson
from datetime import datetime
from loguru import logger
from tortoise import Tortoise, run_async
from tortoise.contrib.pydantic.base import PydanticListModel, PydanticModel
from models import User
from rpc import rpc_functions
from operator import itemgetter as get
from typing import Any
from beartype.roar import BeartypeException


def result_json(result: Any) -> str:
    print(type(result))
    if isinstance(result, list) and isinstance(result[0], PydanticModel):
        return [r.dict() for r in result]
    elif isinstance(result, PydanticListModel) or isinstance(result, PydanticModel):
        return result.dict()
    return result


async def handle_request(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    data: bytes = await reader.readuntil(b"\r\n")
    message = orjson.loads(data.strip().decode("utf-8"))

    function, args = get("function", "args")(message)
    logger.info(f"{function} called with {args}")

    handler = rpc_functions.get(function)
    if handler is not None:
        try:
            value = await handler(*args)
            value_json = result_json(value)
            return_value = {
                "success": True,
                "time": datetime.now(),
                "value": value_json
            }
        except BeartypeException:
            return_value = {
                "success": False,
                "error": "You messed up your types!"
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

    user = await User.create(username="gurleen", password="password")
    await user.save()

    user2 = await User.create(username="trey", password="password2")
    await user2.save()

    logger.info("Starting async event loop")
    server = await asyncio.start_server(handle_request, '127.0.0.1', 5000)
    async with server:
        logger.info("Server started.")
        await server.serve_forever()


run_async(main())