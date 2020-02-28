import curses
from random import randint
from math import sqrt
from copy import copy

news = []

KEY_Q = 113

world_height = 30
world_width = 60

class Creature:
    pass

def chase(c,t, world_map, tiles):
    oldy = c.y
    oldx = c.x
    if c.x > t.x:
        c.x -= 1
    if c.x < t.x:
        c.x += 1
    if c.y < t.y:
        c.y += 1
    if c.y > t.y:
        c.y -= 1

    if c.x == t.x and c.y == t.y:
        t.hp -= 1
        news.append("ow")
        c.x = oldx
        c.y = oldy

    if not walkable(world_map, tiles, c.x, c.y):
        c.x = oldx
        c.y = oldy


def distance(c1, c2):
    a = abs(c2.x - c1.x)
    b = abs(c2.y - c1.y)
    distance = sqrt(a**2 + b**2)
    return distance

class Tile:
    def __init__(self, tile, walkable):
        self.walkable = walkable
        self.tile = tile

def set_color(color_number, r, g, b):
    curses.init_color(color_number, r, g, b)
    curses.init_pair(color_number, color_number, curses.COLOR_BLACK)

def on_screen(x,y):
    off_screen = x < 0 or x >= world_width or y < 0 or y >= world_height
    return not off_screen

def walkable(world_map, tiles, x, y):
    if not on_screen(x, y):
        return False
    # Get the tile number at y,x on the world map
    tnum = world_map[y][x]
    # Look up that tile in the tile list
    tile = tiles[tnum]

    return tile.walkable

def main(screen):
    curses.curs_set(False)  # Disable blinking cursor

    #initialize colors
    set_color(1, 800, 200, 150)
    set_color(3, 0, 900, 0)

    inp = 0

    player = Creature()
    player.x = 35
    player.y = 22
    player.color = 1
    player.looks = "@"
    player.hp = 5
    creatures = [player]
    for x in range(5):
        goblin = Creature()
        goblin.x = randint(0,world_width - 1)
        goblin.y = randint(0,world_height - 1)
        goblin.looks = "G"
        goblin.color = 3
        goblin.hp = 2
        creatures.append(goblin)

    world_map = [[0 for x in range(world_width)] for y in range(world_height)]

    tiles = { 0:  Tile(".",True),
              1:  Tile("#", False) }

    for n in range(10):
        # Pick a random spot on the map
        x = randint(0, world_width - 1)
        y = randint(0, world_height - 1)
        # change the tile at that spot on the world map to 1
        world_map[y][x] = 1


    while (inp != KEY_Q):  # Quit game if player presses "q"
        screen.clear()

        keyboard_input(creatures, inp, player, world_map, tiles)

        # Draw the tiles
        for y in range(len(world_map)):
            for x in range(len(world_map[0])):
                cur_tile_num = world_map[y][x]
                cur_tile = tiles[cur_tile_num]
                screen.addstr(y, x, cur_tile.tile, curses.color_pair(0))




        goblins = filter(lambda c: c.looks == "G", creatures)
        for g in goblins:
            chase(g, player, world_map, tiles)

        # loop over the creatures list
        for c in creatures:
            # do screen.addstr using the properties of each creature
            screen.addstr(c.y, c.x, c.looks, curses.color_pair(c.color))

        if news != []:
            n = 0

            n2 = copy(news)
            n2.reverse()
            n2 = n2[:5]

            for x in n2:
                screen.addstr(world_height + 1 + n, 0, x, curses.color_pair(0))
                n += 1

        screen.addstr(world_height, 0, "you have " + str(player.hp) + " health", curses.color_pair(1))

        screen.refresh()

        if player.hp < 1:
            return

        inp = screen.getch()


def keyboard_input(creatures, inp, player, world_map, tiles):
    oldy = player.y
    oldx = player.x
    if inp == curses.KEY_DOWN:
        player.y = player.y + 1
    elif inp == curses.KEY_UP:
        player.y = player.y - 1
    elif inp == curses.KEY_LEFT:
        player.x = player.x - 1
    elif inp == curses.KEY_RIGHT:
        player.x = player.x + 1
    for c in creatures:
        if player.x == c.x and c.y == player.y and player != c:
            creatures.remove(c)
            player.x = oldx
            player.y = oldy

    if not walkable(world_map, tiles, player.x, player.y):
        player.x = oldx
        player.y = oldy


curses.wrapper(main)