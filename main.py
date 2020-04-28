import curses
from random import randint
from math import sqrt
import gglobals
from display import initialize_colors, draw_screen
from gglobals import world_width, world_height, KEY_Q

class Creature:
    pass

class Item:
    def __init__(self, x, y, looks, name, color, amount=1):
        self.x = x
        self.y = y
        self.looks = looks
        self.name = name
        self.color = color
        self.amount = amount
def attack(c, t):
    player_roll = randint(1,20)
    monster_roll = randint(1, 20)
    if c.speed + player_roll >= t.speed + monster_roll:
        # roll for damage against t
        damage = c.strength + randint(1, 2)
        t.hp -= damage
        # Update gglobals.news with information about the attack
        gglobals.news.append("%s hits %s for %d damage" % (c.name, t.name, damage))

    else:
        gglobals.news.append("%s misses %s" % (c.name, t.name))

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
        gglobals.news.append("I can see!!!!")
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
    initialize_colors()

    inp = 0

    creatures, player, tiles, world_map, items = initialize_world()
    sword = Item(player.x - 2, player.y, "$", "money", 1, 5)
    sword2 = Item(player.x - 1, player.y, "$", "money", 1, 10)
    items.append(sword)
    items.append(sword2)

    gglobals.news.append("Welcome to RidgeRogue II")

    while (inp != KEY_Q):  # Quit game if player presses "q"
        screen.clear()

        b_roll = randint(1, 10)
        if b_roll < 3:
            b = make_boulder(player.x, player.y - 30)
            creatures.append(b)

        keyboard_input(creatures, inp, player, world_map, tiles, items)

        tick_creatures(creatures, player, tiles, world_map)

        draw_screen(creatures, player, screen, tiles, world_map, items)

        if player.hp < 1:
            return

        inp = screen.getch()

def plop_mountain(row, start_x, end_x):
    for x in range(start_x, end_x + 1):
        row[x] = 1

def make_path(world):
    start_x = 60
    gap_width = 6
    min_gap_width = 5
    max_gap_width = 60
    for row in world:
        start_x += randint(-1, 1)
        gap_width += randint(-1, 1)
        if gap_width < min_gap_width:
            gap_width = min_gap_width
        if gap_width > max_gap_width:
            gap_width = max_gap_width
        plop_mountain(row, 0, start_x)
        plop_mountain(row, start_x + gap_width + 1, len(row) - 1)

def initialize_world():
    player = make_player()
    creatures = [player]
    items = []

    world_map = [[0 for x in range(world_width)] for y in range(world_height)]
    tiles = {0: Tile(".", True),
             1: Tile("#", False)}
    make_path(world_map)
    make_random_rocks(world_map)

    for x in range(200):
        while True:
            random_x = randint(0, world_width - 1)
            random_y = randint(0, world_height - 1)
            t = world_map[random_y][random_x]
            if t == 0:
                break
        goblin = make_goblin(random_x, random_y)
        creatures.append(goblin)
    for x in range(200):
        while True:
            random_x = randint(0, world_width - 1)
            random_y = randint(0, world_height - 1)
            t = world_map[random_y][random_x]
            if t == 0:
                break
        scorpion = make_scorpion(random_x, random_y)
        creatures.append(scorpion)

    for x in range(0,len(world_map[0])):
        if world_map[player.y][x] == 0:
            player.x = x
    return creatures, player, tiles, world_map, items


def fall(b, world_map, creatures):
    # Move the boulder down
    b.y += 1
    # Loop over all creatures
    for c in creatures:
        # If the creature and the boulder are in the same spot
        if (c.y == b.y and c.x == b.x) and (c != b):
            # Run the attack function.
            attack(b, c)
            # Put the boulder back where it was
            b.y -= 1




def tick_creatures(creatures, player, tiles, world_map):
    enemies = filter(lambda c: c.looks in ["g", "s", "o"], creatures)
    for g in enemies:
        if g.mode == "wander":
            wander(g, player, world_map, tiles)
        if g.mode == "chase":
            chase(g, player, world_map, tiles)
        if g.mode == "fall":
            fall(g, world_map, creatures)

def make_random_rocks(world_map):
    for n in range(250):
        # Pick a random spot on the map
        x = randint(0, world_width - 1)
        y = randint(0, world_height - 1)
        # change the tile at that spot on the world map to 1
        world_map[y][x] = 1

def make_player():
    player = Creature()
    player.x = 300
    player.y = 150
    player.color = 1
    player.looks = "@"
    player.hp = 15
    player.speed = 10
    player.strength = 1
    player.name = "Mr Gerald Mc Gee"
    player.target = None
    player.mode = None
    player.inventory = []
    player.gold = 0
    return player

def make_scorpion(x,y):
    scorpion = Creature()
    scorpion.x = x
    scorpion.y = y
    scorpion.looks = "s"
    scorpion.color = 4
    scorpion.hp = 2
    scorpion.speed = 11
    scorpion.mode = "wander"
    scorpion.strength = -1
    scorpion.target = None
    scorpion.name = "Scorpio"
    return scorpion

def make_boulder(x, y):
    boulder = Creature()
    boulder.x = x
    boulder.y = y
    boulder.looks = "o"
    boulder.color = 3
    boulder.hp = 15
    boulder.speed = 20
    boulder.strength = 15
    boulder.target = None
    boulder.mode = "fall"
    boulder.name = "Big Rock"
    return boulder

    
def make_goblin(x,y):
    goblin = Creature()
    goblin.x = x
    goblin.y = y
    goblin.looks = "g"
    goblin.color = 3
    goblin.hp = 2
    goblin.speed = 9
    goblin.strength = 0
    goblin.target = None
    goblin.mode = "wander"
    goblin.name = "Gobbo"
    return goblin

def keyboard_input(creatures, inp, player, world_map, tiles, items):
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
                gold_roll = randint(1, 100)
                if gold_roll < 50:
                    amount = randint(1, 2)
                    gold = Item(c.x, c.y, "$", "money", 4, amount)
                    items.append(gold)
    if not walkable(world_map, tiles, player.x, player.y):
        player.x = oldx
        player.y = oldy

    for i in items:
        if player.x == i.x and player.y == i.y:
            pick_up_item(i, items, player)


def pick_up_item(i, items, player):
    items.remove(i)
    if i.name == "money":
        player.gold += i.amount
    else:
        player.inventory.append(i)


curses.wrapper(main)