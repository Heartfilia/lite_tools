import re
try:
    from pydantic import BaseModel
except ImportError:
    from lite_tools.utils.pip_ import install

    install('pydantic')
    from pydantic import BaseModel


class Rule(BaseModel):
    split: str = " "
    long: str = "-"
    short: str = "."


_base_morse = {
    "A": "01",
    "B": "1000",
    "C": "1010",
    "D": "100",
    "E": "0",
    "F": "0010",
    "G": "110",
    "H": "0000",
    "I": "00",
    "J": "0111",
    "K": "101",
    "L": "0100",
    "M": "11",
    "N": "10",
    "O": "111",
    "P": "0110",
    "Q": "1101",
    "R": "010",
    "S": "000",
    "T": "1",
    "U": "001",
    "V": "0001",
    "W": "011",
    "X": "1001",
    "Y": "1011",
    "Z": "1100",
    "0": "11111",
    "1": "01111",
    "2": "00111",
    "3": "00011",
    "4": "00001",
    "5": "00000",
    "6": "10000",
    "7": "11000",
    "8": "11100",
    "9": "11110",
    ".": "010101",
    ",": "110011",
    "?": "001100",
    "'": "011110",
    "!": "101011",
    "/": "10010",
    "(": "10110",
    ")": "101101",
    "&": "01000",
    ":": "111000",
    ";": "101010",
    "=": "10001",
    "+": "01010",
    "-": "100001",
    "_": "001101",
    '"': "010010",
    "$": "0001001",
    "@": "011010"
}

cache = {}
for key, value in _base_morse.items():
    cache[value] = key


def _to_bin(string: str) -> str:
    r_list = []
    for ind, c in enumerate(string):
        string_16 = ("00" + hex(ord(c)))[-4:]   # 获取16进制
        string_2 = bin(int(string_16, 16))[2:]  # 获取2进制的编码
        # 上面为啥不一次性转成2进制呢 因为有些特殊符号需要额外在16进制那里补0 所以就分开写的
        r_list.append(string_2)
    return "".join(r_list)


def morse_encode(string: str, rule: Rule = Rule()) -> str:
    result = []
    list_string = list(re.sub(r"\s+", "", string).upper())
    for char in list_string:
        bin_string = _base_morse.get(char) or _to_bin(char)
        result.append(bin_string.replace("0", rule.short).replace("1", rule.long))
    return rule.split.join(result)


def morse_decode(string: str, rule: Rule = Rule()) -> str:
    result = []
    each_rule = string.split(rule.split)
    for morse in each_rule:
        temp = re.sub(r"\s+", "", morse).replace(rule.short, "0").replace(rule.long, "1")
        if temp in cache:
            result.append(cache[temp])
            continue
        char = chr(int(temp, 2)) if temp else ""
        result.append(char)
    return "".join(result)
