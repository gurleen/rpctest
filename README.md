# rpctest

This is a proof-of-concept RPC server + demo app built with Python and asyncio. 

## Motivation

I've run into a lot of situations where desired business logic doesn't map perfectly onto REST principles.
More often than not, that means your REST API will have to include some RPC-like endpoints. _At that point, why
not just build your whole API using RPC?_

This project is an exploration of RPC and how it might be used to build backends for web and mobile apps, faster.

## Architecture 

Procedures are defined in the `functions` packages and are decorated with `@remote_proc`. The function (including it's arguments and 
return type) should be annotated with PEP 484 type annotations. This allows `beartype` to check argument types at runtime.

```python
from framework import remote_proc

@remote_proc
def add(x: int, y: int) -> int:
    return x + y
```

A user can then open a TCP connection at port 5000 and send a procedure call request like this:

```json
{
    "function": "add",
    "args": [1, 2],
    "token": "<AUTH_TOKEN>"
}
```

(`token` is a reserved space for providing an auth token. It is provided globally during the lifetime of the request
from `framework.context_vars.auth_token`.)

The server will return the result of the procedure call:

```json
{
    "success": true,
    "time": "2021-12-18T18:07:28.718815", 
    "value": 3
}
```

If an error occured during the request, a response like this will be returned:

```json
{
    "success": false,
    "error": "<error message>"
}
```

### Dependency Injection

As syntactic sugar for functions, you can define functions which return commonly used parameters, such as the current user, using 
the `Depends` class. `Depends` takes a function which gets executed at the time of the function call. This is a late-bound parameter
default, which is not natively supported in Python. This is possible because of the dynamic nature of the procedure call.

Define a function that provides this value:

```python
from framework.context_vars import auth_token 

async def current_user() -> User:
    return await User.get_user_from_token(auth_token.get())
```

Then, define a function and set a parameter's default value to an instance of Depends:

```python
@remote_proc
async def login_required(user: User = Depends(current_user)) -> User:
    ...
```

The framework will, before calling `login_required`, resolve any dependencies by calling their related function.
This helps you write less boilerplate code for commonly used tasks. In the future, `Depends` will be able to consume
arguments from the request. For example, you could write your function to accept a `User` object while only requiring a
`user_id: int` from the request.

## Requirements

Install requirements by running:

```bash
pip install -r requirements.txt
```

## Usage

Tested with Python 3.9.9 on macOS 12.0.1 (Apple Silicon).

```bash
python3 app.py
```

```bash
python3 client.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)