#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date : 2019-09-17
import asyncio
from random import randint

import aioredis

from context import SharedContext


async def try_to_lock(seq):
    redis_conn = await aioredis.create_redis_pool('redis://192.168.50.93:6379')
    lock_key = 'redis_lock'
    print('seq:{}'.format(seq))
    async with SharedContext(redis_conn, lock_key):
        await asyncio.sleep(randint(1, 3))

    print('complete')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tasks = [try_to_lock(x) for x in range(10)]
    loop.run_until_complete(asyncio.gather(*tasks))
