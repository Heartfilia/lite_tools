import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from lite_tools import WrapJson
from lite_tools.exceptions.DictExceptions import TemplateFormatError, NotJsonException


class TestWrapJson(unittest.TestCase):
    def test_projection_nested_and_collection_types(self):
        wrap = WrapJson({'id': int, 'profile': {'name': str}, 'tags': list})
        data = {'id': 1, 'profile': {'name': 'A', 'extra': 2}, 'tags': ['x'], 'extra': 3}
        self.assertEqual(wrap.get_all(data), {'id': 1, 'profile': {'name': 'A'}, 'tags': ['x']})

    def test_keys_never_execute_and_preserve_special_characters(self):
        keys = ["' + (print('EXECUTED') or '') + '", 'a.b[0]', "quote'", 'back\\slash', '中文', 123]
        template = {key: str for key in keys}
        data = {key: 'value' for key in keys}
        with patch('builtins.print') as printed:
            self.assertEqual(WrapJson(template).get_all(data), data)
        printed.assert_not_called()

    def test_ellipsis_requires_present_scalar(self):
        wrap = WrapJson({'v': ...})
        self.assertEqual(wrap.get_all({'v': None}), {'v': None})
        self.assertEqual(wrap.get_all({}), {})
        self.assertEqual(wrap.get_all({'v': []}), {})

    def test_filter_list_and_empty_inputs(self):
        wrap = WrapJson({'id': int})
        self.assertEqual(wrap.get_all([{'id': 1}, {'id': True}, [{'id': 2}], {'x': 3}]), [{'id': 1}, {'id': 2}])
        self.assertEqual(wrap.get_all([]), [])
        self.assertEqual(wrap.get_all({}), {})
        self.assertEqual(wrap.get_all('{"id": 1}'), {'id': 1})
        with self.assertRaises(NotJsonException):
            wrap.get_all('null')

    def test_list_template_and_no_input_aliasing(self):
        wrap = WrapJson({'items': [{'id': int}]})
        self.assertEqual(wrap.get_all({'items': [{'id': 1, 'x': 2}, {'id': 2}]}), {'items': [{'id': 1}]})
        self.assertEqual(WrapJson([int, str]).get_all([1, 'a', 3]), [1, 'a'])
        data = {'values': [1]}
        result = WrapJson({'values': list}).get_all(data)
        result['values'].append(2)
        self.assertEqual(data['values'], [1])

    def test_invalid_templates_and_concurrent_results(self):
        with self.assertRaises(TemplateFormatError):
            WrapJson({'id': 1})
        wrap = WrapJson({'id': int})
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda n: wrap.get_all([{'id': n}]), range(30)))
        self.assertEqual(results, [[{'id': n}] for n in range(30)])
