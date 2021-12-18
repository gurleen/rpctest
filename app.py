from tortoise import run_async
from framework.server import main

import functions

run_async(main())
