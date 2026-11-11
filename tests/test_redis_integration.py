"""Opt-in Redis integration; only namespaced keys are touched, never FLUSHDB.

Set LITE_TOOLS_REDIS_TEST_URL to a dedicated test Redis URL to enable.
"""
import os
import unittest
import uuid

from lite_tools.tools.sql.lite_redis import BloomFilter, LiteRedis
from lite_tools.tools.core.lite_cache import LiteCacher


@unittest.skipUnless(os.environ.get('LITE_TOOLS_REDIS_TEST_URL'), '未配置 Redis 测试实例')
class TestRedisIntegration(unittest.TestCase):
    def test_commands_scan_bloom_and_cache(self):
        db = LiteRedis(os.environ['LITE_TOOLS_REDIS_TEST_URL'], keep_waiting=False)
        prefix = 'lite_tools_test:' + uuid.uuid4().hex
        try:
            self.assertTrue(db.ping())
            self.assertTrue(db.set(prefix + ':value', 'hello', ex=60))
            self.assertEqual(db.get(prefix + ':value'), 'hello')
            self.assertEqual(db.incrby(prefix + ':counter'), 1)
            db.hset(prefix + ':hash', mapping={'field': 'value'})
            self.assertEqual(list(db.hscan_iter(prefix + ':hash')), [('field', 'value')])
            with db.pipeline() as pipeline:
                pipeline.set(prefix + ':pipeline', 'ok', ex=60)
                self.assertEqual(pipeline.execute(), [True])
            self.assertIn(prefix + ':value', list(db.scan_iter(match=prefix + ':*', count=1)))
            bloom = BloomFilter(db, prefix + ':bloom', block_num=2, bit_size=1024)
            self.assertFalse(bloom.exists('value'))
            bloom.insert('value')
            self.assertTrue(bloom.exists('value'))
            bloom.remove()
            self.assertFalse(bloom.exists('value'))
            cache = LiteCacher(sync_redis=db.redis)
            calls = []
            @cache.cached(prefix + ':cache', main_key=['user_id'])
            def user(user_id):
                calls.append(user_id)
                return {'id': user_id}
            self.assertEqual(user(1), {'id': 1})
            self.assertEqual(user(user_id=1), {'id': 1})
            self.assertEqual(user(2), {'id': 2})
            self.assertEqual(calls, [1, 2])
        finally:
            # Exact randomized namespace, no database-wide deletion.
            for key in db.scan_iter(match=prefix + ':*'):
                db.delete(key)
            db.close()
