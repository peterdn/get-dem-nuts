import enum
import io
import os
import random
import time

import pygame as pg

from geometry import Direction, pdist, Point, Rotation
from map import MAP
from squirrel import Squirrel
from world import World


SCREEN_WIDTH = 672
SCREEN_HEIGHT = 512
SCREENRECT = pg.rect.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
TILE_WIDTH = 32
TILE_HEIGHT = 32
SCREEN_WIDTH_TILES = int(SCREENRECT.width / TILE_WIDTH)
SCREEN_HEIGHT_TILES = int(SCREENRECT.height / TILE_HEIGHT)

ASSETS = [
    "squirrel", "greysquirrel", "tree", "nut", "water",
    {'name': "summerground", 'mirror': True},
]


class Action(enum.Enum):
    SPACE = 1
    F = 2


class Nut:
    __next_id = 1

    def __init__(self, x, y):
        self.pos = Point(x, y)
        self.id = Nut.__next_id
        Nut.__next_id += 1
        self.energy = 200


class Game:
    NUT_SPAWN_RATE = 8000
    ENERGY_LOSS_RATE = 500
    N_SQUIRRELS = 5
    NPC_MOVE_RATE = 1000
    N_GROUND_TILES = 30

    def __init__(self, screen):
        self.scheduled_events = []

        self.world = World(MAP, self.N_GROUND_TILES)
        self._generate_squirrels()

        self._schedule_event(self.energy_loss, Game.ENERGY_LOSS_RATE)
        self._schedule_event(self.spawn_nut, Game.NUT_SPAWN_RATE)

        self.screen = screen
        self.assets = {}

        self.energy_bar = pg.Surface((200, 30))
        self.over = False

        self.new_pos = Point(self.world.squirrel.pos.x, self.world.squirrel.pos.y)

        self.random_seed = time.time_ns()

    def _generate_squirrels(self):
        squirrels = []
        for i in range(Game.N_SQUIRRELS):
            squirrel = Squirrel(self.world.random_point(), Direction.RIGHT)
            self.world.squirrels.append(squirrel)

        self._schedule_event(self.tick_squirrels, Game.NPC_MOVE_RATE)

    def _schedule_event(self, action, period):
        event = ScheduledEvent(action, period)
        self.scheduled_events.append(event)

    def energy_loss(self, event, current_timestamp):
        self.world.squirrel.energy -= int((current_timestamp - event.last_timestamp) / self.ENERGY_LOSS_RATE)

    def spawn_nut(self, event, current_timestamp):
        nutx = random.randint(0, self.world.WIDTH_TILES-1)
        nuty = random.randint(0, self.world.HEIGHT_TILES-1)
        nut = Nut(nutx, nuty)
        self.world.nuts[nut.id] = nut

    def tick_squirrels(self, event, current_timestamp):
        for squirrel in self.world.squirrels:
            squirrel.tick(self)

    def load_assets(self):
        current_path = os.path.abspath(os.path.curdir)
        assets_path = os.path.join(current_path, 'assets')
        print("Loading assets...")
        for asset in ASSETS:
            asset_filename = asset if isinstance(asset, str) else asset['name']
            f = os.path.join(assets_path, f"{asset_filename}.png")
            try:
                surface = pg.image.load(f)
            except pg.error:
                raise SystemExit(f"Failed to load asset {asset_filename}: {pg.get_error()}")
            surface = surface.convert_alpha()
            if surface.get_width() > TILE_WIDTH:
                self.assets[asset_filename] = []
                for i in range(int(surface.get_width() / TILE_WIDTH)):
                    r = pg.rect.Rect(i*TILE_WIDTH, 0, TILE_WIDTH, TILE_HEIGHT)
                    subsurface = surface.subsurface(r)
                    self.assets[asset_filename].append(subsurface)
                    if isinstance(asset, dict) and asset['mirror']:
                        self.assets[asset_filename].append(pg.transform.flip(subsurface, True, False))
            else:
                self.assets[asset_filename] = surface.convert_alpha()

    def _draw_image_at(self, image, x, y, frame=None):
        if isinstance(image, str):
            image = self.assets[image]
        px = x * TILE_WIDTH
        py = y * TILE_HEIGHT

        if frame is not None:
            image = image[frame]

        self.screen.blit(image, (px, py))

    def render_map(self):
        for x in range(SCREEN_WIDTH_TILES):
            for y in range(SCREEN_HEIGHT_TILES):
                (mapx, mapy) = (self.world.squirrel.pos.x + x - int(SCREEN_WIDTH_TILES / 2), self.world.squirrel.pos.y + y - int(SCREEN_HEIGHT_TILES / 2 - 1))
                if mapx < 0 or mapx >= self.world.WIDTH_TILES or mapy < 0 or mapy >= self.world.HEIGHT_TILES:
                    self._draw_image_at('water', x, y)
                elif self.world.MAP[mapy][mapx] == '.':
                    frame = self.world.GROUND_LAYER[mapy][mapx]['tileidx']
                    self._draw_image_at('summerground', x, y, frame=frame)
                elif self.world.MAP[mapy][mapx] == '#':
                    self._draw_image_at('tree', x, y)

    def render(self):
        self.screen.fill((30, 182, 202))

        self.render_map()

        # Render nuts
        for nut in self.world.nuts.values():
            sx = nut.pos.x + int(SCREEN_WIDTH_TILES / 2) - self.world.squirrel.pos.x
            sy = nut.pos.y + int(SCREEN_HEIGHT_TILES / 2 - 1) - self.world.squirrel.pos.y
            if sx < 0 or sx >= SCREEN_WIDTH_TILES or sy < 0 or sy >= SCREEN_HEIGHT_TILES:
                continue
            self._draw_image_at('nut', sx, sy)

        # Draw other squirrels
        for squirrel in self.world.squirrels:
            sx = squirrel.pos.x + int(SCREEN_WIDTH_TILES / 2) - self.world.squirrel.pos.x
            sy = squirrel.pos.y + int(SCREEN_HEIGHT_TILES / 2 - 1) - self.world.squirrel.pos.y
            if sx < 0 or sx >= SCREEN_WIDTH_TILES or sy < 0 or sy >= SCREEN_HEIGHT_TILES:
                continue
            self._draw_image_at('greysquirrel', sx, sy, frame=squirrel.facing.value-1)

        # Draw squirrel
        self._draw_image_at(
            'squirrel',
            int(SCREEN_WIDTH_TILES / 2),
            int(SCREEN_HEIGHT_TILES / 2 - 1),
            frame=self.world.squirrel.facing.value-1)

        # Draw energy bar
        self.energy_bar.fill((0, 0, 128))
        fill_width = (self.world.squirrel.energy / 1000) * 196
        self.energy_bar.fill((255, 255, 0), pg.rect.Rect(2, 2, fill_width, 26))
        self.screen.blit(self.energy_bar, (20, 466))

        pg.display.update()

    def _move_in_direction(self, pos, direction):
        x, y = pos.x, pos.y
        if direction == Direction.UP:
            y -= 1
        elif direction == Direction.DOWN:
            y += 1
        elif direction == Direction.LEFT:
            x -= 1
        elif direction == Direction.RIGHT:
            x += 1
        x = max(0, min(self.world.WIDTH_TILES - 1, x))
        y = max(0, min(self.world.HEIGHT_TILES - 1, y))
        return Point(x, y)

    def move(self, key):
        self.new_pos = self._move_in_direction(self.new_pos, key)

    def face(self, key):
        self.world.squirrel.facing = key

    def rotate(self, direction):
        # TODO: fix spritesheet and enum order to allow
        # this to be done with modular arithmetic.
        if direction == Rotation.Clockwise:
            rmap = {
                Direction.DOWN: Direction.LEFT,
                Direction.LEFT: Direction.UP,
                Direction.UP: Direction.RIGHT,
                Direction.RIGHT: Direction.DOWN,
            }
        elif direction == Rotation.CounterClockwise:
            rmap = {
                Direction.DOWN: Direction.RIGHT,
                Direction.RIGHT: Direction.UP,
                Direction.UP: Direction.LEFT,
                Direction.LEFT: Direction.DOWN,
            }
        self.world.squirrel.facing = rmap[self.world.squirrel.facing]

    def _facing(self):
        facingx, facingy = self.world.squirrel.pos.x, self.world.squirrel.pos.y
        if self.world.squirrel.facing == Direction.UP:
            return facingx, facingy-1
        elif self.world.squirrel.facing == Direction.DOWN:
            return facingx, facingy+1
        elif self.world.squirrel.facing == Direction.LEFT:
            return facingx-1, facingy
        elif self.world.squirrel.facing == Direction.RIGHT:
            return facingx+1, facingy

    def action(self, action):
        facingx, facingy = self._facing()
        if action == Action.SPACE:
            nut_id = None
            for nut in self.world.nuts.values():
                if nut.pos.x == facingx and nut.pos.y == facingy:
                    nut_id = nut.id
                    self.world.squirrel.set_energy(self.world.squirrel.energy + nut.energy)

            if nut_id is not None:
                del self.world.nuts[nut_id]
        elif action == Action.F:
            if facingx >= 0 and facingy >= 0 and facingx < self.world.WIDTH_TILES and facingy < self.world.HEIGHT_TILES:
                self.world.GROUND_LAYER[facingy][facingx]['tileidx'] = random.randint(0, self.N_GROUND_TILES-1)

    def tick(self):
        # If we're moving in a cardinal direction, face that way
        if self.new_pos.x != self.world.squirrel.pos.x and self.new_pos.y == self.world.squirrel.pos.y:
            self.world.squirrel.facing = Direction.LEFT if self.new_pos.x < self.world.squirrel.pos.x else Direction.RIGHT
        elif self.new_pos.y != self.world.squirrel.pos.y and self.new_pos.x == self.world.squirrel.pos.x:
            self.world.squirrel.facing = Direction.UP if self.new_pos.y < self.world.squirrel.pos.y else Direction.DOWN

        if self.world.can_move_to(self.new_pos):
            energy_cost = pdist(self.new_pos, self.world.squirrel.pos)
            self.world.squirrel.set_energy(self.world.squirrel.energy - energy_cost)
            self.world.squirrel.pos = self.new_pos

        if self.world.squirrel.energy <= 0:
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

    pg.display.set_caption('get dem nuts')

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
                if event.key == pg.K_ESCAPE:
                    doquit = True
                if event.key == pg.K_q:
                    game.rotate(Rotation.CounterClockwise)
                if event.key == pg.K_e:
                    game.rotate(Rotation.Clockwise)
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
                if event.key == pg.K_f:
                    game.action(Action.F)

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
