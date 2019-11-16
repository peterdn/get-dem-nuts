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
    "squirrel", "greysquirrel", "tree", "nut", "grass",
]


class Direction(enum.Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Action(enum.Enum):
    SPACE = 1


class Squirrel:
    def __init__(self, x, y, facing):
        self.x = x
        self.y = y
        self.facing = facing
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
    ENERGY_LOSS_RATE = 500
    N_SQUIRRELS = 5
    NPC_MOVE_RATE = 1000

    def __init__(self, screen):
        from map import MAP
        self.MAP = MAP
        self.MAP_WIDTH_TILES = len(self.MAP[0])
        self.MAP_HEIGHT_TILES = len(self.MAP)

        self.scheduled_events = []
        self._schedule_event(self.energy_loss, Game.ENERGY_LOSS_RATE)
        self._schedule_event(self.spawn_nut, Game.NUT_SPAWN_RATE)

        self.screen = screen
        self.assets = {}
        self.squirrel = Squirrel(14, 14, Direction.DOWN)
        self.nuts = {}
        self.squirrels = self._generate_squirrels()
        self.energy_bar = pg.Surface((200, 30))
        self.over = False

        self.newx, self.newy = self.squirrel.x, self.squirrel.y

    def _generate_squirrels(self):
        squirrels = []
        for i in range(Game.N_SQUIRRELS):
            sx = random.randint(0, self.MAP_WIDTH_TILES-1)
            sy = random.randint(0, self.MAP_HEIGHT_TILES-1)
            squirrel = Squirrel(sx, sy, Direction.RIGHT)
            squirrels.append(squirrel)

        self._schedule_event(self.move_squirrels, Game.NPC_MOVE_RATE)
        return squirrels

    def _schedule_event(self, action, period):
        event = ScheduledEvent(action, period)
        self.scheduled_events.append(event)

    def energy_loss(self, event, current_timestamp):
        self.squirrel.energy -= int((current_timestamp - event.last_timestamp) / self.ENERGY_LOSS_RATE)

    def spawn_nut(self, event, current_timestamp):
        nutx = random.randint(0, self.MAP_WIDTH_TILES-1)
        nuty = random.randint(0, self.MAP_HEIGHT_TILES-1)
        nut = Nut(nutx, nuty)
        self.nuts[nut.id] = nut

    def move_squirrels(self, event, current_timestamp):
        for squirrel in self.squirrels:
            squirrel.facing = Direction(random.randint(1, 4))
            newx, newy = self._move(squirrel.x, squirrel.y, squirrel.facing)
            if self._can_move_to(newx, newy):
                squirrel.x, squirrel.y = newx, newy

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
            surface = surface.convert_alpha()
            if surface.get_width() > TILE_WIDTH:
                self.assets[asset] = []
                for i in range(int(surface.get_width() / TILE_WIDTH)):
                    r = pg.rect.Rect(i*TILE_WIDTH, 0, TILE_WIDTH, TILE_HEIGHT)
                    subsurface = surface.subsurface(r)
                    self.assets[asset].append(subsurface)
            else:
                self.assets[asset] = surface.convert_alpha()

    def _draw_image_at(self, image, x, y, frame=None):
        if isinstance(image, str):
            image = self.assets[image]
        px = x * TILE_WIDTH
        py = y * TILE_HEIGHT

        if frame is not None:
            image = image[frame]

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

        # Draw other squirrels
        for squirrel in self.squirrels:
            sx = squirrel.x + int(SCREEN_WIDTH_TILES / 2) - self.squirrel.x
            sy = squirrel.y + int(SCREEN_HEIGHT_TILES / 2 - 1) - self.squirrel.y
            if sx < 0 or sx >= SCREEN_WIDTH_TILES or sy < 0 or sy >= SCREEN_HEIGHT_TILES:
                continue
            self._draw_image_at('greysquirrel', sx, sy, frame=squirrel.facing.value-1)

        # Draw squirrel
        self._draw_image_at(
            'squirrel',
            int(SCREEN_WIDTH_TILES / 2),
            int(SCREEN_HEIGHT_TILES / 2 - 1),
            frame=self.squirrel.facing.value-1)

        # Draw energy bar
        self.energy_bar.fill((0, 0, 128))
        fill_width = (self.squirrel.energy / 1000) * 196
        self.energy_bar.fill((255, 255, 0), pg.rect.Rect(2, 2, fill_width, 26))
        self.screen.blit(self.energy_bar, (20, 466))

        pg.display.update()

    def _move(self, x, y, direction):
        if direction == Direction.UP:
            y -= 1
        elif direction == Direction.DOWN:
            y += 1
        elif direction == Direction.LEFT:
            x -= 1
        elif direction == Direction.RIGHT:
            x += 1
        x = max(0, min(self.MAP_WIDTH_TILES-1, x))
        y = max(0, min(self.MAP_HEIGHT_TILES-1, y))
        return x, y

    def move(self, key):
        self.newx, self.newy = self._move(self.newx, self.newy, key)

    def face(self, key):
        self.squirrel.facing = key

    def _facing(self):
        facingx, facingy = self.squirrel.x, self.squirrel.y
        if self.squirrel.facing == Direction.UP:
            return facingx, facingy-1
        elif self.squirrel.facing == Direction.DOWN:
            return facingx, facingy+1
        elif self.squirrel.facing == Direction.LEFT:
            return facingx-1, facingy
        elif self.squirrel.facing == Direction.RIGHT:
            return facingx+1, facingy

    def action(self, action):
        facingx, facingy = self._facing()
        if action == Action.SPACE:
            nut_id = None
            for nut in self.nuts.values():
                if nut.x == facingx and nut.y == facingy:
                    nut_id = nut.id
                    self.squirrel.set_energy(self.squirrel.energy + nut.energy)

            if nut_id is not None:
                del self.nuts[nut_id]

    def _can_move_to(self, x, y):
        if x < 0 or x >= self.MAP_WIDTH_TILES or y < 0 or y >= self.MAP_HEIGHT_TILES:
            return False
        if x == self.squirrel.x and y == self.squirrel.y:
            return False
        for squirrel in self.squirrels:
            if (x, y) == (squirrel.x, squirrel.y):
                return False
        return True

    def tick(self):
        # If we're moving in a cardinal direction, face that way
        if self.newx != self.squirrel.x and self.newy == self.squirrel.y:
            self.squirrel.facing = Direction.LEFT if self.newx < self.squirrel.x else Direction.RIGHT
        elif self.newy != self.squirrel.y and self.newx == self.squirrel.x:
            self.squirrel.facing = Direction.UP if self.newy < self.squirrel.y else Direction.DOWN

        if self._can_move_to(self.newx, self.newy):
            if self.newx != self.squirrel.x:
                self.squirrel.x = self.newx
                self.squirrel.set_energy(self.squirrel.energy - 1)
            if self.newy != self.squirrel.y:
                self.squirrel.y = self.newy
                self.squirrel.set_energy(self.squirrel.energy - 1)
        else:
            self.newx, self.newy = self.squirrel.x, self.squirrel.y

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
                if event.key in [pg.K_UP, pg.K_w]:
                    game.face(Direction.UP)
                if event.key in [pg.K_DOWN, pg.K_s]:
                    game.face(Direction.DOWN)
                if event.key in [pg.K_LEFT, pg.K_a]:
                    game.face(Direction.LEFT)
                if event.key in [pg.K_RIGHT, pg.K_d]:
                    game.face(Direction.RIGHT)
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
