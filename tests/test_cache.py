import asyncio
import inspect
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import AsyncMock, MagicMock, patch

import redis

from lite_tools.tools.core.lite_cache import LiteCacher


class TestLiteCacher(unittest.TestCase):
    def test_main_key_uses_bound_call_arguments(self):
        cache = LiteCacher()
        calls = []
        @cache.cached('users', main_key=['user_id'])
        def user(user_id, ignored=0):
            calls.append(user_id)
            return {'user_id': user_id}
        self.assertEqual(user(user_id=1), {'user_id': 1})
        self.assertEqual(user(2), {'user_id': 2})
        self.assertEqual(user(1, ignored=99), {'user_id': 1})
        self.assertEqual(calls, [1, 2])

    def test_argument_defaults_keyword_order_and_types(self):
        cache = LiteCacher()
        calls = []
        @cache.cached('values')
        def value(a=1, b=2):
            calls.append((a, b))
            return len(calls)
        self.assertEqual(value(), value(b=2, a=1))
        self.assertEqual(value(1, 2), value(a=1))
        self.assertNotEqual(value(True), value(1))
        self.assertNotEqual(value('1'), value(1))

    def test_separator_collision_and_mapping_canonicalization(self):
        cache = LiteCacher()
        @cache.cached('join')
        def join(a, b): return (a, b)
        self.assertNotEqual(join('a;b', 'c'), join('a', 'b;c'))
        signature = inspect.signature(lambda x: x)
        self.assertEqual(cache.cal_redis_key_name('dict', signature, None, {'a': 1, 'b': 2}),
                         cache.cal_redis_key_name('dict', signature, None, {'b': 2, 'a': 1}))

    def test_instances_and_functions_are_isolated(self):
        cache = LiteCacher()
        class User:
            def __init__(self, name): self.name = name
            @cache.cached('shared')
            def get(self): return self.name
        first, second = User('A'), User('B')
        self.assertEqual(first.get(), 'A')
        self.assertEqual(second.get(), 'B')
        @cache.cached('shared')
        def one(): return 1
        @cache.cached('shared')
        def two(): return 2
        self.assertEqual(one(), 1)
        self.assertEqual(two(), 2)

    def test_missing_main_key_raises(self):
        cache = LiteCacher()
        @cache.cached('bad', main_key=['typo'])
        def value(user_id): return user_id
        with self.assertRaises(ValueError):
            value(1)

    def test_closure_instances_do_not_share_results(self):
        cache = LiteCacher()
        def factory(user_id):
            @cache.cached('closure')
            def value(): return user_id
            return value
        first, second = factory(1), factory(2)
        self.assertEqual(first(), 1)
        self.assertEqual(second(), 2)

    def test_kwargs_main_key(self):
        cache = LiteCacher()
        @cache.cached('kw', main_key=['user_id'])
        def value(**kwargs): return kwargs['user_id']
        self.assertEqual(value(user_id=1), 1)
        self.assertEqual(value(user_id=2), 2)

    def test_unsupported_values_bypass_instead_of_colliding(self):
        cache = LiteCacher()
        @cache.cached('objects')
        def value(obj): return id(obj)
        a, b = object(), object()
        self.assertEqual(value(a), id(a))
        self.assertEqual(value(b), id(b))
        self.assertEqual(cache._mid_hash, {})

    def test_uncopyable_result_does_not_break_function(self):
        class Result:
            def __deepcopy__(self, memo):
                raise TypeError('not copyable')
        cache = LiteCacher()
        @cache.cached('uncopyable')
        def value(): return Result()
        self.assertIsInstance(value(), Result)
        self.assertEqual(cache._mid_hash, {})

    def test_memory_ttl_copy_and_bound(self):
        cache = LiteCacher(max_entries=2)
        calls = []
        @cache.cached('ttl', ttl=5)
        def value(n):
            calls.append(n)
            return {'n': n}
        with patch('lite_tools.tools.core.lite_cache.time.monotonic', return_value=10):
            result = value(1)
            result['n'] = 999
            self.assertEqual(value(1), {'n': 1})
            value(2)
            value(3)
            self.assertLessEqual(len(cache._mid_hash), 2)
        with patch('lite_tools.tools.core.lite_cache.time.monotonic', return_value=16):
            value(3)
        self.assertEqual(calls.count(3), 2)

    def test_concurrent_expiry_has_no_keyerror(self):
        cache = LiteCacher()
        @cache.cached('threads', ttl=1)
        def value(n): return n
        with patch('lite_tools.tools.core.lite_cache.time.monotonic', return_value=0):
            value(1)
        with patch('lite_tools.tools.core.lite_cache.time.monotonic', return_value=2):
            with ThreadPoolExecutor(max_workers=8) as pool:
                self.assertEqual(list(pool.map(value, [1] * 50)), [1] * 50)

    def test_broken_redis_cache_is_miss(self):
        backend = MagicMock()
        backend.get.side_effect = [redis.exceptions.ConnectionError(), b'broken json', b'{}']
        cache = LiteCacher(sync_redis=backend)
        @cache.cached('failover')
        def value(n): return n
        for n in range(3):
            self.assertEqual(value(n), n)

    def test_invalid_ttl(self):
        for ttl in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                LiteCacher().cached('ttl', ttl=ttl)


class TestAsyncLiteCacher(unittest.IsolatedAsyncioTestCase):
    async def test_sync_backend_runs_outside_event_loop_thread(self):
        import threading
        current = threading.get_ident()
        backend = MagicMock()
        threads = []
        def get(key):
            threads.append(threading.get_ident())
            return None
        backend.get.side_effect = get
        cache = LiteCacher(sync_redis=backend)
        @cache.cached('thread')
        async def value(n): return n
        self.assertEqual(await value(1), 1)
        self.assertTrue(threads)
        self.assertNotEqual(threads[0], current)

    async def test_async_memory(self):
        cache = LiteCacher()
        calls = []
        @cache.cached('async', main_key=['user_id'])
        async def value(user_id):
            calls.append(user_id)
            return user_id
        self.assertEqual(await value(1), 1)
        self.assertEqual(await value(user_id=1), 1)
        self.assertEqual(await value(2), 2)
        self.assertEqual(calls, [1, 2])

    async def test_async_backend_and_sync_memory_fallback(self):
        backend = MagicMock()
        backend.get = AsyncMock(return_value=None)
        backend.set = AsyncMock()
        cache = LiteCacher(async_redis=backend)
        @cache.cached('a')
        async def async_value(n): return n
        @cache.cached('s')
        def sync_value(n): return n
        self.assertEqual(await async_value(1), 1)
        backend.set.assert_awaited_once()
        self.assertEqual(sync_value(2), 2)
        self.assertEqual(sync_value(2), 2)
        self.assertEqual(len(cache._mid_hash), 1)

    async def test_async_redis_failure_and_cancellation(self):
        backend = MagicMock()
        backend.get = AsyncMock(side_effect=redis.exceptions.TimeoutError())
        backend.set = AsyncMock()
        cache = LiteCacher(async_redis=backend)
        @cache.cached('fail')
        async def value(): return 7
        self.assertEqual(await value(), 7)
        backend.get.side_effect = asyncio.CancelledError()
        with self.assertRaises(asyncio.CancelledError):
            await value()
