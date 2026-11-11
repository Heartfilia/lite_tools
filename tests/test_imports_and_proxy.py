import asyncio
import unittest
import subprocess
import sys
from unittest.mock import AsyncMock, MagicMock, patch

from lite_tools.tools.core.ip_info import check_proxy


class TestImports(unittest.TestCase):
    def test_wildcard_import(self):
        namespace = {}
        exec('from lite_tools import *', namespace)
        self.assertIn('SqlString', namespace)
        self.assertIn('LiteRedis', namespace)

    def test_basic_import_without_optional_yaml_or_mysql(self):
        code = '''
import builtins
original = builtins.__import__
def blocked(name, *args, **kwargs):
    if name in ('yaml', 'pymysql', 'aiomysql', 'dbutils') or name.startswith(('pymysql.', 'dbutils.')):
        error = ModuleNotFoundError('test missing optional dependency')
        error.name = name.split('.')[0]
        raise error
    return original(name, *args, **kwargs)
builtins.__import__ = blocked
from lite_tools import *
client = LiteRedis('redis://localhost', keep_waiting=False)
assert client.host == 'localhost'
assert SqlString('t').count() == 'SELECT COUNT(*) FROM `t`;'
'''
        result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


class TestProxy(unittest.IsolatedAsyncioTestCase):
    async def test_connection_awaited_and_closed(self):
        writer = MagicMock()
        with patch('telnetlib3.open_connection', new=AsyncMock(return_value=(MagicMock(), writer))) as connect:
            self.assertTrue(await check_proxy('http://user:secret@[::1]:8080'))
        connect.assert_awaited_once_with(host='::1', port=8080, connect_maxwait=3)
        writer.close.assert_called_once()

    async def test_invalid_ports_never_connect(self):
        with patch('telnetlib3.open_connection', new=AsyncMock()) as connect:
            for proxy in ('host:0', 'host:65536', 'host:no', '', None):
                self.assertFalse(await check_proxy(proxy))
        connect.assert_not_awaited()

    async def test_timeout_and_cancellation(self):
        with patch('telnetlib3.open_connection', new=AsyncMock(side_effect=asyncio.TimeoutError())):
            self.assertFalse(await check_proxy('localhost:80'))
        with patch('telnetlib3.open_connection', new=AsyncMock(side_effect=asyncio.CancelledError())):
            with self.assertRaises(asyncio.CancelledError):
                await check_proxy('localhost:80')
