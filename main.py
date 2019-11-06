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


class Action(enum.Enum):
    SPACE = 1


class Squirrel:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 1000

    def set_energy(self, energy):
        self.energy = min(1000, max(0, energy))


class Nut:
    __next_id = 1

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = Nut.__next_id
        Nut.__next_id += 1
        self.energy = 200


class Game:
    NUT_SPAWN_RATE = 8000

    def __init__(self, screen):
        self.screen = screen
        self.assets = {}
        self.squirrel = Squirrel(14, 14)
        self.nuts = {}
        self.energy_bar = pg.Surface((200, 30))
        self.over = False

        from map import MAP
        self.MAP = MAP
        self.MAP_WIDTH_TILES = len(self.MAP[0])
        self.MAP_HEIGHT_TILES = len(self.MAP)

        self.scheduled_events = []
        self._schedule_event(self.energy_loss, 800)
        self._schedule_event(self.spawn_nut, Game.NUT_SPAWN_RATE)

    def _schedule_event(self, action, period):
        event = ScheduledEvent(action, period)
        self.scheduled_events.append(event)

    def energy_loss(self, event, current_timestamp):
        print(self.squirrel.energy)
        self.squirrel.energy -= int((current_timestamp - event.last_timestamp) / 800)

    def spawn_nut(self, event, current_timestamp):
        nutx = random.randint(0, self.MAP_WIDTH_TILES-1)
        nuty = random.randint(0, self.MAP_HEIGHT_TILES-1)
        nut = Nut(nutx, nuty)
        self.nuts[nut.id] = nut

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

        # Render nuts
        for nut in self.nuts.values():
            sx = nut.x + int(SCREEN_WIDTH_TILES / 2) - self.squirrel.x
            sy = nut.y + int(SCREEN_HEIGHT_TILES / 2 - 1) - self.squirrel.y
            if sx < 0 or sx >= SCREEN_WIDTH_TILES or sy < 0 or sy >= SCREEN_HEIGHT_TILES:
                continue
            self._draw_image_at('nut', sx, sy)

        # Draw squirrel
        self._draw_image_at(
            'squirrel',
            int(SCREEN_WIDTH_TILES / 2),
            int(SCREEN_HEIGHT_TILES / 2 - 1))

        # Draw energy bar
        self.energy_bar.fill((0, 0, 128))
        fill_width = (self.squirrel.energy / 1000) * 196
        self.energy_bar.fill((255, 255, 0), pg.rect.Rect(2, 2, fill_width, 26))
        self.screen.blit(self.energy_bar, (20, 466))

        pg.display.update()

    def move(self, key):
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
        self.squirrel.set_energy(self.squirrel.energy - 2)

    def action(self, action):
        if action == Action.SPACE:
            nut_id = None
            for nut in self.nuts.values():
                if nut.x == self.squirrel.x and nut.y == self.squirrel.y:
                    nut_id = nut.id
                    self.squirrel.set_energy(self.squirrel.energy + nut.energy)

            if nut_id is not None:
                del self.nuts[nut_id]

    def tick(self):
        if self.squirrel.energy <= 0:
            self.over = True


def current_time_ms():
    return int(time.time() * 1000)


class ScheduledEvent:
    def __init__(self, action, period):
        self.action = action
        self.period = period
        self.last_timestamp = current_time_ms()


def main():
    pg.init()

    screen = pg.display.set_mode(SCREENRECT.size, 0)
    clock = pg.time.Clock()

    game = Game(screen)
    game.load_assets()

    last_move_timestamp = 0
    MOVE_KEYPRESS_INTERVAL = 100

    doquit = False
    while not doquit:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                doquit = True
            if event.type == pg.KEYDOWN:
                if event.key in [pg.K_q, pg.K_ESCAPE]:
                    doquit = True
                if event.key == pg.K_SPACE:
                    game.action(Action.SPACE)

        if not game.over:
            current_timestamp = current_time_ms()

            if current_timestamp > last_move_timestamp + \
                    MOVE_KEYPRESS_INTERVAL:
                keystate = pg.key.get_pressed()
                direction = None
                if keystate[pg.K_UP] or keystate[pg.K_w]:
                    game.move(Direction.UP)
                    last_move_timestamp = current_timestamp
                if keystate[pg.K_DOWN] or keystate[pg.K_s]:
                    game.move(Direction.DOWN)
                    last_move_timestamp = current_timestamp
                if keystate[pg.K_LEFT] or keystate[pg.K_a]:
                    game.move(Direction.LEFT)
                    last_move_timestamp = current_timestamp
                if keystate[pg.K_RIGHT] or keystate[pg.K_d]:
                    game.move(Direction.RIGHT)
                    last_move_timestamp = current_timestamp

            for scheduled_event in game.scheduled_events:
                if current_timestamp > scheduled_event.last_timestamp + \
                                       scheduled_event.period:
                    scheduled_event.action(scheduled_event, current_timestamp)
                    scheduled_event.last_timestamp = current_timestamp

            game.tick()

        game.render()

        clock.tick(30)

    pg.quit()


if __name__ == '__main__':
    main()
