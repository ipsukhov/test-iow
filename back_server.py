import asyncio
import datetime
from aiohttp import web

@asyncio.coroutine
def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "{}\nHello, {}! It's {}.\n".format(
        request.method, name, str(datetime.datetime.now())
    )
    return web.Response(body=text.encode('utf-8'))


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('*', '/{name:.*}', handle)

    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 8088)
    print("Server started at http://127.0.0.1:8088")
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

