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

def attack(c, t):
    player_roll = randint(1,20)
    monster_roll = randint(1, 20)
    if c.speed + player_roll >= t.speed + monster_roll:
        # roll for damage against t
        damage = c.strength + randint(1, 2)
        t.hp -= damage
        # Update news with information about the attack
        news.append("%s hits %s for %d damage" % (c.name, t.name, damage))

    else:
        news.append("%s misses %s" % (c.name, t.name))

def can_see(c, t):

    if c.x == t.x or c.y == t.y:
        return True
    else:
        return False

def wander(c,t, world_map, tiles):
    move = randint(1, 4)
    oldx = c.x
    oldy = c.y
    if move == 1:
        c.y -=1
    if move == 2:
        c.y +=1
    if move == 3:
        c.x -=1
    if move == 4:
        c.x +=1
    if not walkable(world_map, tiles, c.x, c.y):
        c.x = oldx
        c.y = oldy
    # if c can see player
    if can_see(c, t):
        news.append("I can see!!!!")
        # set target to player
        c.target = t
        # set mode to chase
        c.mode = "chase"


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
        attack(c,t)
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
    set_color(4, 1000, 1000, 0)

    inp = 0

    player = Creature()
    player.x = 35
    player.y = 22
    player.color = 1
    player.looks = "@"
    player.hp = 7
    player.speed = 10
    player.strength = 1
    player.name = "Mr Gerald Mc Gee"
    player.target = None
    player.mode = None
    creatures = [player]
    for x in range(5):
        goblin = Creature()
        goblin.x = randint(0,world_width - 1)
        goblin.y = randint(0,world_height - 1)
        goblin.looks = "g"
        goblin.color = 3
        goblin.hp = 2
        goblin.speed = 9
        goblin.strength = 0
        goblin.target = None
        goblin.mode = "wander"
        goblin.name = "Gobbo"
        creatures.append(goblin)
        
        scorpion = Creature()
        scorpion.x = randint(0,world_width - 1)
        scorpion.y = randint(0,world_height - 1)
        scorpion.looks = "s"
        scorpion.color = 4
        scorpion.hp = 2
        scorpion.speed = 12
        scorpion.mode = "wander"
        scorpion.strength = -1
        scorpion.target = None
        scorpion.name = "Scorpio"
        creatures.append(scorpion)

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




        enemies = filter(lambda c: c.looks in ["g", "s"], creatures)
        for g in enemies:
            if g.mode == "wander":
                wander(g, player, world_map, tiles)
            if g.mode == "chase":
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
            player.x = oldx
            player.y = oldy
            attack(player, c)
            if c.hp <= 0:
                creatures.remove(c)
    if not walkable(world_map, tiles, player.x, player.y):
        player.x = oldx
        player.y = oldy


curses.wrapper(main)