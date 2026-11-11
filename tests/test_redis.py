import itertools
import json
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

import redis

from lite_tools.tools.sql.lite_redis import BloomFilter, LiteProxy, LiteRedis


class TestLiteRedis(unittest.TestCase):
    def client(self, **kwargs):
        return LiteRedis(timeout=0, **kwargs)

    def test_no_driver_write_replay_and_timeout_override(self):
        db = self.client(socket_timeout=17)
        options = db.redis.connection_pool.connection_kwargs
        self.assertEqual(options['socket_timeout'], 17)
        self.assertEqual(options['retry']._retries, 0)
        self.assertFalse(options.get('retry_on_timeout', False))

    def test_write_executed_once_when_response_is_lost(self):
        db = self.client()
        writes = []
        def incrby(name, amount):
            writes.append(amount)
            raise redis.exceptions.TimeoutError('response lost after commit')
        with self.assertRaises(redis.exceptions.TimeoutError):
            db._redis_option(incrby, 'counter', 1)
        self.assertEqual(writes, [1])

    def test_read_retries_bounded(self):
        db = self.client(retry_attempts=3)
        calls = []
        def get(name):
            calls.append(name)
            if len(calls) < 3:
                raise redis.exceptions.ConnectionError('offline')
            return 'ok'
        self.assertEqual(db._redis_option(get, 'key'), 'ok')
        self.assertEqual(len(calls), 3)
        calls.clear()
        db.keep_waiting = False
        with self.assertRaises(redis.exceptions.ConnectionError):
            db._redis_option(get, 'key')
        self.assertEqual(len(calls), 1)

    def test_permanent_errors_and_unknown_commands_do_not_retry(self):
        db = self.client()
        for error in (redis.exceptions.ResponseError('WRONGTYPE'), redis.exceptions.AuthenticationError('denied'),
                      TypeError('bad argument'), KeyboardInterrupt()):
            calls = []
            def get(name):
                calls.append(name)
                raise error
            with self.subTest(error=error), self.assertRaises(type(error)):
                db._redis_option(get, 'k')
            self.assertEqual(len(calls), 1)
        command = MagicMock(side_effect=redis.exceptions.ConnectionError())
        with self.assertRaises(redis.exceptions.ConnectionError):
            db._redis_option(command)
        self.assertEqual(command.call_count, 1)

    def test_read_exhaustion_and_retry_budget(self):
        db = self.client(retry_attempts=3)
        calls = []
        def get(name):
            calls.append(name)
            raise redis.exceptions.ConnectionError('offline')
        with self.assertRaises(redis.exceptions.ConnectionError):
            db._redis_option(get, 'k')
        self.assertEqual(len(calls), 3)
        db.timeout = 10
        db._retry_deadline = 5
        calls.clear()
        with self.assertRaises(redis.exceptions.ConnectionError):
            db._redis_option(get, 'k')
        self.assertEqual(len(calls), 1)

    def test_no_argument_delegation_and_attributes(self):
        db = self.client()
        db._redis = MagicMock()
        db._redis.connection_pool = object()
        self.assertIs(db.ping(), db.redis.ping.return_value)
        db.redis.ping.assert_called_once_with()
        self.assertIs(db.pipeline(), db.redis.pipeline.return_value)
        self.assertIs(db.connection_pool, db.redis.connection_pool)
        with self.assertRaises(AttributeError):
            getattr(db, '_missing')

    def test_scan_retries_current_page_not_entire_iterator(self):
        db = self.client()
        calls = []
        def scan(**kwargs):
            calls.append(kwargs['cursor'])
            if len(calls) == 1:
                return 5, ['a']
            if len(calls) == 2:
                raise redis.exceptions.TimeoutError()
            return 0, ['b']
        db._redis = MagicMock()
        db._redis.scan = scan
        self.assertEqual(list(db.scan_iter(match='prefix:*')), ['a', 'b'])
        self.assertEqual(calls, [0, 5, 5])

    def test_hash_and_sorted_scan_return_shapes(self):
        db = self.client()
        db._redis = MagicMock()
        db.redis.hscan.return_value = (0, {'a': 'b'})
        db.redis.zscan.return_value = (0, [('a', 1.0)])
        db.redis.sscan.return_value = (0, ['a'])
        self.assertEqual(list(db.hscan_iter('hash')), [('a', 'b')])
        self.assertEqual(list(db.zscan_iter('sorted')), [('a', 1.0)])
        self.assertEqual(list(db.sscan_iter('set')), ['a'])

    def test_url_parsing_credentials_ipv6_tls_and_query(self):
        cases = [
            ('redis://localhost', 'localhost', 6379, 0, None, None),
            ('redis://:p%40ss@localhost:6380/2', 'localhost', 6380, 2, None, 'p@ss'),
            ('rediss://user:p%3Aa@[::1]:6380/3?socket_timeout=7&decode_responses=False', '::1', 6380, 3, 'user', 'p:a'),
        ]
        for url, host, port, db, user, password in cases:
            client = self.client(path=url)
            self.assertEqual((client.host, client.port, client.db, client.username, client.password),
                             (host, port, db, user, password))
        self.assertIs(client.redis.connection_pool.connection_class, redis.connection.SSLConnection)
        self.assertFalse(client.decode)
        self.assertEqual(client.redis.connection_pool.connection_kwargs['socket_timeout'], 7)

    def test_yaml_safe_and_optional(self):
        try:
            import yaml
        except ImportError:
            self.skipTest('PyYAML 未安装')
        with patch('builtins.open', return_value=StringIO('host: localhost\nport: 6380\nkwargs:\n  socket_timeout: 9\n')):
            client = self.client(path='config.yaml')
        self.assertEqual(client.port, 6380)
        self.assertEqual(client.redis.connection_pool.connection_kwargs['socket_timeout'], 9)
        with patch('builtins.open', return_value=StringIO('host: !!python/object/apply:builtins.eval ["40+2"]')):
            with self.assertRaises(yaml.constructor.ConstructorError):
                self.client(path='config.yaml')

    def test_invalid_config_fails_fast(self):
        for config in ([], None, {'kwargs': []}, {'host': ''}, {'port': 0}, {'db': -1}, {'decode': 'false'}):
            with patch('builtins.open', return_value=StringIO(json.dumps(config))):
                with self.subTest(config=config), self.assertRaises(ValueError):
                    self.client(path='config.json')
        for kwargs in ({'retry_attempts': 0}, {'retry_deadline': -1}, {'timeout': -1},
                       {'port': 0}, {'decode_responses': 'false'}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                LiteRedis(**kwargs)

    def test_hset_does_not_pass_unsupported_items_default(self):
        db = self.client()
        db._redis = MagicMock()
        db.hset('h', mapping={'a': 'b'})
        db.redis.hset.assert_called_with('h', key=None, value=None, mapping={'a': 'b'})

    def test_proxy_bytes_and_scheme(self):
        self.assertEqual(LiteProxy._trans_type('string', b'127.0.0.1:80'), 'http://127.0.0.1:80')
        self.assertEqual(LiteProxy._trans_type('string', 'socks5://localhost:80'), 'socks5://localhost:80')


class TestBloomFilter(unittest.TestCase):
    def test_membership_requires_all_bits_for_even_and_odd_seed_counts(self):
        for seeds in ([5, 7], [5, 7, 11]):
            for bits in itertools.product((0, 1), repeat=len(seeds)):
                server = MagicMock()
                server.getbit.side_effect = bits
                bloom = BloomFilter(server, 'bloom', bit_size=1024, seeds=seeds)
                self.assertEqual(bloom.exists('item'), all(bits))

    def test_roundtrip_and_remove_exact_partitions(self):
        data = {}
        server = MagicMock()
        server.setbit.side_effect = lambda key, bit, value: data.__setitem__((key, bit), value)
        server.getbit.side_effect = lambda key, bit: data.get((key, bit), 0)
        bloom = BloomFilter(server, 'bloom*', block_num=3, bit_size=1024)
        self.assertFalse(bloom.exists('value'))
        bloom.insert('value')
        self.assertTrue(bloom.exists('value'))
        bloom.remove()
        self.assertEqual([call.args for call in server.delete.call_args_list], [('bloom*:0',), ('bloom*:1',), ('bloom*:2',)])

    def test_invalid_configuration(self):
        for kwargs in ({'bit_size': 0}, {'bit_size': 100}, {'bit_size': 1 << 33},
                       {'block_num': 0}, {'block_num': 257}, {'seeds': []}, {'seeds': [5, 5]}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                BloomFilter(MagicMock(), 'bloom', **kwargs)
