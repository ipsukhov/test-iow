Test task (code example).

The goal is: making an asynchronous caching HTTP-proxy server.
Frameworks/libraries allowed: Twisted, Tornado, asyncio.

Details:
* caching GET/POST requests (with params/data) for remote upstream if response code is within 200-299, cache lifetime is 60 seconds;
* all other requests must be proxied transparently.

===

Comments:

Using Python 3.4, asyncio, aiohttp and asyncio-redis.

Files:
* back_server.py - aiohttp example server, plays role of the remote upstream.
* server.py - main file. Execute: "python server.py" or "python server.py [HOSTNAME]". Possibly, it is not fully transparent in all possible cases, but in real life this will be done by nginx.
* requirements.txt and pytest.ini - no special comments.
* tests.py - there are no courutine tests (mocking them was too tedious for practising).
