import aiohttp
import asyncio
import asyncio_redis
import json
import sys
from aiohttp import web

if len(sys.argv) > 1:
    TARGET = sys.argv[1]
else:
    TARGET = '127.0.0.1:8088'

REDIS_CONNECTION = {
    'host': '127.0.0.1',
    'port': 6379
}
CACHE_LIFETIME = 60  # Seconds


def build_cache_key(method, path, query_string, post_data):
    return '|'.join((
        method, path,
        query_string
        if method == 'GET'
        else '&'.join('{}={}'.format(k, v) for k, v in post_data.items())
    ))


@asyncio.coroutine
def cached_getpost_proxy(request, cache, cache_lifetime=CACHE_LIFETIME):
    """
    Caches successfull HTTP requests to remote upstream with 200-299 status.
    Caching depends on GET/POST params.

    :type request: aiohttp.web.Request
    :param cache: cache instance with get/post interface
    :param cache_lifetime: cache lifetime in seconds
    :type cache_lifetime: int
    :rtype: aiohttp.web.Request
    """
    if request.method not in ('GET', 'POST'):
        response = yield from transparent_proxy(request)
        return response

    yield from request.post()  # Needed to construct request.POST
    cache_key = build_cache_key(
        request.method, request.path, request.query_string, request.POST
    )
    cached_response = yield from cache.get(cache_key)

    if cached_response:
        response = web.Response(**json.loads(cached_response))
    else:
        response = yield from transparent_proxy(request)
        if 200 <= response.status <= 299:
            yield from cache.set(
                cache_key,
                json.dumps({
                    'status': response.status,
                    'headers': dict(response.headers),
                    'text': response.text
                }),
                expire=cache_lifetime
            )
    return response


@asyncio.coroutine
def transparent_proxy(request, target=TARGET):
    """
    :type request: aiohttp.web.Request
    :param target: remote upstream
    :type target: str or unicode
    :rtype: aiohttp.web.Request
    """
    with aiohttp.ClientSession(cookies=request.cookies) as session:
        yield from request.post()  # Needed to construct request.POST
        response = yield from session.request(
            method = request.method,
            url = 'http://{}{}'.format(target, request.path),
            params=request.GET,
            data=request.POST,
            headers=request.headers,
            version=request.version
        )
    text = yield from response.text()
    return web.Response(
        headers = response.headers,
        text = text,
        status = response.status
    )


@asyncio.coroutine
def not_cached_route(request):
    response = yield from transparent_proxy(request)
    return response


@asyncio.coroutine
def cached_route(request):
    cache = yield from asyncio_redis.Connection.create(**REDIS_CONNECTION)
    response = yield from cached_getpost_proxy(request, cache)
    return response


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('*', '/api/slow-endpoint/', cached_route)
    app.router.add_route('*', '/{path:.*}', not_cached_route)

    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 8080)
    print('Server started at http://127.0.0.1:8080')
    return srv


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
