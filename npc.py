import functools
import math

sign = functools.partial(math.copysign, 1)


class NPC:
    def __init__(self):
        self.x, self.y = 0, 0


def find_path(fromx, fromy, tox, toy, impassable=None):
    if impassable is None:
        impassable = ''

    if fromx == tox:
        delta = int(sign(toy - fromy))
        return [(fromx, y) for y in range(fromy, toy + delta, delta)]

    gradient = (toy - fromy) / (tox - fromx)
    print(f"gradient = {gradient}")

    path = []
    x, y = fromx, fromy
    if abs(gradient) > 1:
        while y != toy:
            path.append((round(x), y))
            y += int(sign(toy - fromy))
            x += sign(toy - fromy) * ((tox - fromx) / (toy - fromy))
    else:
        while x != tox:
            path.append((x, round(y)))
            x += int(sign(tox - fromx))
            y += sign(tox - fromx) * gradient

    path.append((tox, toy))
    return path
