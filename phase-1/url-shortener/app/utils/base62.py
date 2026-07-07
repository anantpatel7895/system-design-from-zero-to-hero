

BASE62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def encode(num: int) -> str:

    if num == 0:
        return BASE62[0]

    chars = []

    while num > 0:
        num, remainder = divmod(num, 62)
        chars.append(BASE62[remainder])

    return "".join(reversed(chars))


def decode(code: str) -> int:

    num = 0

    for char in code:
        num *= 62
        num += BASE62.index(char)

    return num