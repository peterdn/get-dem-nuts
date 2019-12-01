import enum
import io
import os
import random
import time

import pygame as pg

from geometry import Direction, pdist, Point, Rotation
from fox import Fox
from map import MAP
from nut import Nut
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
    "squirrel", "greysquirrel", "tree", "nut", "water", "fox", "sun",
    {'name': "summerground", 'mirror': True},
    "bignut", "bignutgrey",
]


class Action(enum.Enum):
    SPACE = 1
    F = 2
    C = 3


class Season(enum.Enum):
    SUMMER = 1
    WINTER = 2


class Game:
    NUT_SPAWN_RATE = 5000
    ENERGY_LOSS_RATE = 500
    ENERGY_LOSS_PER_SEC = 16
    ENERGY_LOSS_MULTIPLIER = 1
    N_SQUIRRELS = 5
    NPC_MOVE_RATE = 1000
    FOX_MOVE_RATE = 150
    N_GROUND_TILES = 30
    ROUND_DURATION = {
        Season.SUMMER: 1*50*1000,
        Season.WINTER: 1*30*1000,
    }
    DAY_TRANSITION_RATE = 50
    DAY_TRANSITION_LENGTH = 1000

    def __init__(self, screen):
        self.font = pg.font.SysFont(pg.font.get_default_font(), 56)

        self.screen = screen
        self.assets = {}

        self.energy_bar = pg.Surface((200, 30))
        self.sunlight_bar = pg.Surface((200, 30))
        self.nightfall_overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
        self._game_over = False

        self.world = World(MAP, self.N_GROUND_TILES)

        self.scheduled_events = []

        self.level = 1
        self.current_season = Season.SUMMER
        self.current_round_elapsed = 0
        self.nightfall = 20
        self.init_season()

        self.new_pos = Point(self.world.squirrel.pos.x, self.world.squirrel.pos.y)

    def nightfall_transition(self, event, current_timestamp):
        if self.nightfall >= self.DAY_TRANSITION_LENGTH / self.DAY_TRANSITION_RATE:
            complete_next_season()
        else:
            self.nightfall += (current_timestamp - event.last_timestamp) / self.DAY_TRANSITION_RATE

    def daylight_transition(self, event, current_timestamp):
        if self.nightfall >= 0:
            self.nightfall -= (current_timestamp - event.last_timestamp) / self.DAY_TRANSITION_RATE

    def next_season(self):
        self.scheduled_events.clear()

        self._schedule_event(self.nightfall_transition, self.DAY_TRANSITION_RATE)
        self._schedule_event(self.complete_next_season, self.DAY_TRANSITION_LENGTH)

    def complete_next_season(self, event, current_timestamp):
        self.scheduled_events.clear()

        if not self.world.is_tree(self.world.squirrel.pos):
            self.over("You got eaten by an owl!")

        if self.current_season == Season.SUMMER:
            self.current_season = Season.WINTER
        elif self.current_season == Season.WINTER:
            self.current_season = Season.SUMMER
            self.level += 1
        self.init_season()

    def init_season(self):
        self._schedule_event(self.daylight_transition, self.DAY_TRANSITION_RATE)
        self._schedule_event(self.update_round_elapsed, 1)
        self._schedule_event(self.energy_loss, Game.ENERGY_LOSS_RATE)
        self._schedule_event(self.tick_squirrels, Game.NPC_MOVE_RATE)
        self._schedule_event(self.tick_foxes, Game.FOX_MOVE_RATE)

        self.current_round_elapsed = 0
        self._init_foxes(self.number_foxes_for_level())
        if self.current_season == Season.SUMMER:
            self._init_squirrels(Game.N_SQUIRRELS)
            self._init_nuts(self.number_nuts_for_level())
            self._schedule_event(self.spawn_nut_event, self.nut_spawn_rate_for_level())
        elif self.current_season == Season.WINTER:
            self._init_squirrels(0)
            self._init_nuts(0)

    def nut_spawn_rate_for_level(self):
        return 5000 + self.level * 2000

    def number_nuts_for_level(self):
        return max(1, 5 - self.level)

    def number_foxes_for_level(self):
        return self.level

    def _init_nuts(self, nnuts):
        for nut in self.world.active_nuts():
            del self.world.nuts[nut.id]
        for i in range(nnuts):
            self.spawn_random_nut()

    def _init_squirrels(self, nsquirrels):
        self.world.squirrels.clear()
        for i in range(nsquirrels):
            squirrel = Squirrel(self.world.random_point(), Direction.RIGHT)
            self.world.squirrels.append(squirrel)

    def _init_foxes(self, nfoxes):
        self.world.foxes.clear()
        for i in range(nfoxes):
            while True:
                pos = self.world.random_point()
                if Fox._can_move_to(self.world, pos):
                    break
            fox = Fox(self.world.random_point(), Direction.DOWN)
            self.world.foxes.append(fox)

    def _schedule_event(self, action, period):
        event = ScheduledEvent(action, period)
        self.scheduled_events.append(event)

    def energy_loss(self, event, current_timestamp):
        energy_loss = int((current_timestamp - event.last_timestamp) / 1000 * self.ENERGY_LOSS_PER_SEC)
        self.world.squirrel.energy -= energy_loss

    def spawn_nut_event(self, event, current_timestamp):
        self.spawn_random_nut()

    def update_round_elapsed(self, event, current_timestamp):
        elapsed = current_timestamp - event.last_timestamp
        self.current_round_elapsed += elapsed
        if self.current_round_elapsed > self.ROUND_DURATION[self.current_season]:
            self.next_season()

    def spawn_random_nut(self):
        nutx = random.randint(0, self.world.WIDTH_TILES-1)
        nuty = random.randint(0, self.world.HEIGHT_TILES-1)
        nut = Nut(nutx, nuty)
        self.world.nuts[nut.id] = nut

    def tick_squirrels(self, event, current_timestamp):
        for squirrel in self.world.squirrels:
            squirrel.tick(self)

    def tick_foxes(self, event, current_timestamp):
        for fox in self.world.foxes:
            fox.tick(self)

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
            if nut.state != Nut.NutState.ACTIVE:
                continue
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

        # Draw foxes
        for fox in self.world.foxes:
            sx = fox.pos.x + int(SCREEN_WIDTH_TILES / 2) - self.world.squirrel.pos.x
            sy = fox.pos.y + int(SCREEN_HEIGHT_TILES / 2 - 1) - self.world.squirrel.pos.y
            if sx < 0 or sx >= SCREEN_WIDTH_TILES or sy < 0 or sy >= SCREEN_HEIGHT_TILES:
                continue
            self._draw_image_at('fox', sx, sy, frame=fox.facing.value-1)

        # Draw squirrel
        self._draw_image_at(
            'squirrel',
            int(SCREEN_WIDTH_TILES / 2),
            int(SCREEN_HEIGHT_TILES / 2 - 1),
            frame=self.world.squirrel.facing.value-1)

        # Draw energy bar
        self.energy_bar.fill((0, 0, 128))
        fill_width = (self.world.squirrel.energy / 1000) * 196
        self.energy_bar.fill((255, 255, 255), pg.rect.Rect(2, 2, fill_width, 26))
        self.screen.blit(self.energy_bar, (20, 466))

        self.render_sunlight_bar()

        self.render_inventory()

        if self.nightfall > 0:
            nightfall_alpha = (self.nightfall / (self.DAY_TRANSITION_LENGTH / self.DAY_TRANSITION_RATE)) * 255
            nightfall_alpha = max(0, min(255, nightfall_alpha))
            self.nightfall_overlay.fill((0, 0, 0, nightfall_alpha))
            self.screen.blit(self.nightfall_overlay, (0, 0))

        if self._game_over:
            self.render_game_over()

        pg.display.update()

    def render_sunlight_bar(self):
        self.sunlight_bar.fill((0, 0, 128))
        x = (self.current_round_elapsed / self.ROUND_DURATION[self.current_season]) * \
            (self.sunlight_bar.get_width() - self.assets['sun'].get_width())
        self.sunlight_bar.blit(self.assets['sun'], (x, 0))
        self.screen.blit(self.sunlight_bar, (240, 466))

    def render_inventory(self):
        if self.world.squirrel.is_carrying_nut():
            nut_image = self.assets['bignut']
        else:
            nut_image = self.assets['bignutgrey']
        self.screen.blit(nut_image, (620, 464))

    def render_game_over(self):
        s = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
        s.fill((50, 50, 50, 224))
        txt = self.font.render(self._game_over, True, (255, 255, 255))
        x = (SCREEN_WIDTH - txt.get_width())/2
        y = (SCREEN_HEIGHT - txt.get_height())/2
        s.blit(txt, (x, y))
        self.screen.blit(s, (0, 0))

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
        facing = Point(facingx, facingy)
        if action == Action.SPACE:
            nut = self.world.is_nut(facing)
            if nut is not None and nut.state == Nut.NutState.ACTIVE:
                self.world.squirrel.set_energy(self.world.squirrel.energy + nut.energy)
                del self.world.nuts[nut.id]
        elif action == Action.C and self.world.is_tree(self.world.squirrel.pos) == self.world.is_tree(facing):
            if self.world.squirrel.is_carrying_nut() and self.world.can_bury_nut(facing):
                nut = self.world.squirrel.carrying_nut
                nut.pos = facing
                nut.state = Nut.NutState.BURIED
                self.world.nuts[nut.id] = nut
                self.world.squirrel.carrying_nut = None
            else:
                nut = self.world.is_nut(facing)
                if nut is not None and not self.world.squirrel.is_carrying_nut():
                    if nut.state == Nut.NutState.ACTIVE:
                        self.world.squirrel.carrying_nut = nut
                        del self.world.nuts[nut.id]
                    elif nut.state == Nut.NutState.BURIED:
                        nut.state = Nut.NutState.ACTIVE
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
            energy_cost = pdist(self.new_pos, self.world.squirrel.pos) * self.ENERGY_LOSS_MULTIPLIER
            self.world.squirrel.set_energy(self.world.squirrel.energy - energy_cost)
            self.world.squirrel.pos = self.new_pos
        else:
            self.new_pos = self.world.squirrel.pos

        if self.world.squirrel.energy <= 0:
            self._game_over = "You ran out of energy and died!"

    def over(self, message):
        self._game_over = message


def current_time_ms():
    return int(time.time() * 1000)


class ScheduledEvent:
    def __init__(self, action, period):
        self.action = action
        self.period = period
        self.last_timestamp = current_time_ms()


def main():
    pg.init()
    pg.font.init()

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
                if event.key == pg.K_c:
                    game.action(Action.C)

        if not game._game_over:
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
