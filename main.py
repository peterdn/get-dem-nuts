import enum
import io
import os
import random
import time

import pygame as pg


SCREEN_WIDTH = 672
SCREEN_HEIGHT = 512
SCREENRECT = pg.rect.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
TILE_WIDTH = 32
TILE_HEIGHT = 32
SCREEN_WIDTH_TILES = int(SCREENRECT.width / TILE_WIDTH)
SCREEN_HEIGHT_TILES = int(SCREENRECT.height / TILE_HEIGHT)

ASSETS = [
    "squirrel", "tree", "nut", "grass",
]


class Direction(enum.Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Squirrel:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.assets = {}
        self.squirrel = Squirrel(14, 14)

        from map import MAP
        self.MAP = MAP
        self.MAP_WIDTH_TILES = len(self.MAP[0])
        self.MAP_HEIGHT_TILES = len(self.MAP)

    def load_assets(self):
        current_path = os.path.abspath(os.path.curdir)
        assets_path = os.path.join(current_path, 'assets')
        print("Loading assets...")
        for asset in ASSETS:
            f = os.path.join(assets_path, f"{asset}.png")
            try:
                surface = pg.image.load(f)
            except pg.error:
                raise SystemExit(f"Failed to load asset {asset}: {pg.get_error()}")
            self.assets[asset] = surface.convert_alpha()

    def _draw_image_at(self, image, x, y):
        if isinstance(image, str):
            image = self.assets[image]
        px = x * TILE_WIDTH
        py = y * TILE_HEIGHT
        self.screen.blit(image, (px, py))

    def render(self):
        self.screen.fill((0, 0, 0))

        for x in range(SCREEN_WIDTH_TILES):
            for y in range(SCREEN_HEIGHT_TILES):
                (mapx, mapy) = (self.squirrel.x + x - int(SCREEN_WIDTH_TILES / 2), self.squirrel.y + y - int(SCREEN_HEIGHT_TILES / 2 - 1))
                if mapx < 0 or mapx >= self.MAP_WIDTH_TILES or mapy < 0 or mapy >= self.MAP_HEIGHT_TILES:
                    continue
                if self.MAP[mapy][mapx] == '.':
                    self._draw_image_at('grass', x, y)
                elif self.MAP[mapy][mapx] == '#':
                    self._draw_image_at('tree', x, y)

        self._draw_image_at(
            'squirrel',
            int(SCREEN_WIDTH_TILES / 2),
            int(SCREEN_HEIGHT_TILES / 2 - 1))

        pg.display.update()

    def move_squirrel(self, key):
        newx, newy = self.squirrel.x, self.squirrel.y
        if key == Direction.UP:
            newy -= 1
        elif key == Direction.DOWN:
            newy += 1
        elif key == Direction.LEFT:
            newx -= 1
        elif key == Direction.RIGHT:
            newx += 1
        newx = max(0, min(self.MAP_WIDTH_TILES-1, newx))
        newy = max(0, min(self.MAP_HEIGHT_TILES-1, newy))
        self.squirrel.x = newx
        self.squirrel.y = newy


def current_time_ms():
    return int(time.time() * 1000)


def main():
    pg.init()

    screen = pg.display.set_mode(SCREENRECT.size, 0)
    clock = pg.time.Clock()

    game = Game(screen)
    game.load_assets()

    last_moved_timestamp = 0
    KEYPRESS_INTERVAL = 100

    doquit = False
    while not doquit:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                doquit = True
            if event.type == pg.KEYDOWN and event.key in [pg.K_q, pg.K_ESCAPE]:
                doquit = True

        current_timestamp = current_time_ms()
        if current_timestamp > last_moved_timestamp + KEYPRESS_INTERVAL:
            keystate = pg.key.get_pressed()
            if keystate[pg.K_UP] or keystate[pg.K_w]:
                game.move_squirrel(Direction.UP)
                last_moved_timestamp = current_timestamp
            if keystate[pg.K_DOWN] or keystate[pg.K_s]:
                game.move_squirrel(Direction.DOWN)
                last_moved_timestamp = current_timestamp
            if keystate[pg.K_LEFT] or keystate[pg.K_a]:
                game.move_squirrel(Direction.LEFT)
                last_moved_timestamp = current_timestamp
            if keystate[pg.K_RIGHT] or keystate[pg.K_d]:
                game.move_squirrel(Direction.RIGHT)
                last_moved_timestamp = current_timestamp

        game.render()

        clock.tick(30)

    pg.quit()


if __name__ == '__main__':
    main()
