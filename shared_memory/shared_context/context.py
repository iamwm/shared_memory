#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date : 2019-08-21
import asyncio
from time import time


class SharedContext(object):
    def __init__(self, redis_conn, lock_name, lock_prefix_name='lock:', timeout=3):
        self.redis_conn = redis_conn
        self.lock_name = lock_prefix_name + lock_name
        self.timeout = timeout
        self.expire_time = None

    async def try_to_lock(self):
        try:
            while True:
                now = time()
                self.expire_time = now + self.timeout + 1
                timeout_duration = self.timeout + 1
                # 此处setnx和setex应该放到一起，避免出现死锁。可以通过lua script完成
                lock_result = await self.redis_conn.setnx(self.lock_name, self.expire_time)
                if lock_result:
                    await self.redis_conn.setex(self.lock_name, timeout_duration, self.expire_time)
                    break
                await asyncio.sleep(0.01)
                # print('lock was token by others')
        except Exception as e:
            print(str(e))

    async def try_to_unlock(self):
        lua_script = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end"
        try:
            unlock_result = await self.redis_conn.eval(lua_script, [self.lock_name], [self.expire_time])
            if not unlock_result:
                print('lock has expired')
            else:
                print('unlock successfully')
        except Exception as e:
            print(str(e))

    async def __aenter__(self):
        await self.try_to_lock()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.try_to_unlock()
