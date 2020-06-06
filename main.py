import curses
from random import randint, choice
from math import sqrt
import gglobals
from display import initialize_colors, draw_screen
from gglobals import world_width, world_height, KEY_Q
from cave import grow_cave

MAX_HEALTH_TIMER = 13



def first(f,l):
    for e in l:
        if f(e):
            return e
    return None

class Creature:
    pass

class Item:
    def __init__(self, x, y, looks, name, color, amount = 1):
        self.x = x
        self.y = y
        self.looks = looks
        self.name = name
        self.color = color
        self.amount = amount

def attack(c, t):
    player_roll = randint(1,20)
    monster_roll = randint(1, 20)
    result = ""
    damage = 0
    if c.speed + player_roll >= t.speed + monster_roll:

        # roll for damage against t
        damage = c.strength + randint(1, 2)
        t.hp -= damage
        # Update gglobals.news with information about the attack
        result = "hit"
    if c.name == "player" or t.name == "player":
        if result == "hit":
            gglobals.news.append("%s hits %s for %d damage" % (c.name, t.name, damage))
        else:
            gglobals.news.append("%s misses %s" % (c.name, t.name))


def can_see(c, t):
    if distance(c, t) < 13:
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
        # set target to player
        c.target = t
        # set mode to chase
        c.mode = "chase"


def chase(c,t, world_map, tiles, creatures, items):
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

    for c2 in creatures:
        if (c2.y == c.y and c2.x == c.x) and (c != c2):
            if c.x == t.x and c.y == t.y:
                attack(c, t)
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
    return x >= 0 and x < world_width and y >= 0 and y < world_height


def walkable(world_map, tiles, x, y):
    if not on_screen(x, y):
        return False
    # Get the tile number at y,x on the world map
    tnum = world_map[y][x]
    # Look up that tile in the tile list
    tile = tiles[tnum]

    return tile.walkable


# Spawn a creature near the player at an appropriate difficulty level
def spawn_monster(creatures, player, world_map, tiles):
    spawn_roll = randint(1, 2)
    # Pick a random valid spot near the player but not visible by the player
    x, y = random_valid_spot(world_map, player, player.y - 75, player.y + 75)
    # Make a creature at that spot
    c = make_goblin(x, y)
    if spawn_roll == 1:
        c = make_scorpion(x, y)
    # Add it to the creature list
    creatures.append(c)
    pass


def limit_hp(player):
    if player.hp > player.maxhp:
        player.hp = player.maxhp



def main(screen):
    curses.curs_set(False)  # Disable blinking cursor
    initialize_colors()

    health_timer = MAX_HEALTH_TIMER


    inp = 0

    creatures, player, tiles, world_map, items, caves = initialize_world()


    gglobals.news.append("Welcome to RidgeRogue II")
    gglobals.news.append("%d" % len(caves))

    while (inp != KEY_Q):  # Quit game if player presses "q"
        screen.clear()

        limit_hp(player)

        health_timer -= 1
        if health_timer == 0:
            health_timer = MAX_HEALTH_TIMER
            player.hp += 1
        spawn_roll = randint(1, 4)
        if spawn_roll == 3 and len(creatures) <= 80:
            pass
            #spawn_monster(creatures, player, world_map, tiles)

        b_roll = randint(1, 10)
        if b_roll < 3:
            wobble = randint(-5, 5)
            b = make_boulder(player.x + wobble, player.y - 30)
            #creatures.append(b)

        keyboard_input(creatures, inp, player, world_map, tiles, items)
        # if player is standing on a cave
        if world_map[player.y][player.x] == 2:
            # get cave map corresponding to that coordinate
            cave = first(lambda c: c[0][0] == player.x and c[0][1] == player.y, caves)
            if cave is not None:
                world_map = make_cave()#cave[1]
                cave_width = len(world_map[0])
                cave_height = len(world_map)
                rx = 75
                ry = 75
                # while rx and ry are on a cave tile
                while world_map[ry][rx] == 1:
                    # generate a random rx and ry
                    rx = randint(0, cave_width)
                    ry = randint(0, cave_height)
                player.x = rx
                player.y = ry
                creatures = [player]
                items = []
            else:
                gglobals.news.append("None!")


        tick_creatures(creatures, player, tiles, world_map, items)
        for c in creatures:
            if c.hp <= 0:
                die(c, creatures, items)

        draw_screen(creatures, player, screen, tiles, world_map, items)

        if player.hp < 1:
            return

        inp = screen.getch()

def plop_mountain(row, start_x, end_x):
    for x in range(start_x, end_x + 1):
        row[x] = 1

def is_touching_path(world_map, x, y):
    try:
    # Get the value at x - 1, y
        left_value = world_map[y][x - 1]
        right_value = world_map[y][x + 1]
        top_value = world_map[y - 1][x]
        bottom_value = world_map[y + 1][x]
        current_value = world_map[y][x]
    except:
        return False
    if current_value == 1 and 0 in [left_value, right_value, top_value, bottom_value]:
        return True
    else:
        return False

def plop_caves(world_map, num_caves):
    valid_caves = []
    for y in range(len(world_map)):
        for x in range(len(world_map[0])):
            if is_touching_path(world_map, x,y):
                valid_caves.append((x,y))

    actual_caves = []
    for x in range(num_caves):
        cave_x, cave_y = choice(valid_caves)
        world_map[cave_y][cave_x] = 2
        actual_caves.append((cave_x,cave_y))
    return actual_caves




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

def old_spawn_code():
    world_map = []
    creatures = None
    for x in range(700):
        random_x, random_y = random_valid_spot(world_map)
        goblin = make_goblin(random_x, random_y)
        creatures.append(goblin)
    for x in range(700):
        while True:
            random_x = randint(0, world_width - 1)
            random_y = randint(0, world_height - 1)
            t = world_map[random_y][random_x]
            if t == 0:
                break
        scorpion = make_scorpion(random_x, random_y)
        creatures.append(scorpion)


def random_valid_spot(world_map, player, min_y, max_y):
    while True:
        random_x = randint(0, world_width - 1)
        random_y = randint(min_y, max_y)
        t = world_map[random_y][random_x]
        dummy = Creature()
        dummy.x = random_x
        dummy.y = random_y

        if t == 0 and distance(dummy, player) > 30:
            break
    return random_x, random_y

def make_cave():
    return grow_cave(150, 150, 1750, 100, death_rate=2, cave_tile=1, empty_tile=0)
    #cave = [[choice([0,0,0,0,0,0,0,0,0,1]) for x in range(1000)] for y in range(1000)]
    #return cave

def initialize_world():
    player = make_player()
    creatures = [player]
    items = []
    world_map = [[0 for x in range(world_width)] for y in range(world_height)]
    tiles = {0: Tile(".", True),
             1: Tile("#", False),
             2: Tile("0", True)}
    make_path(world_map)
    make_random_rocks(world_map)
    caves = plop_caves(world_map, 1000)
    caves = list(map(lambda c: (c, None), caves))

    for x in range(0,len(world_map[0])):
        if world_map[player.y][x] == 0:
            player.x = x
    health_potion = Item(player.x - 1, player.y, "8", "Bubbly dark potion", 4, 0)
    items.append(health_potion)
    return creatures, player, tiles, world_map, items, caves


def fall(b, world_map, creatures, items):
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




def tick_creatures(creatures, player, tiles, world_map, items):
    enemies = filter(lambda c: c.looks in ["g", "s", "o"] and c.hp > 0, creatures)
    for g in enemies:
        if g.mode == "wander":
            wander(g, player, world_map, tiles)
        if g.mode == "chase":
            chase(g, player, world_map, tiles, creatures, items)
        if g.mode == "fall":
            fall(g, world_map, creatures, items)

def make_random_rocks(world_map):
    for n in range(250):
        # Pick a random spot on the map
        x = randint(0, world_width - 1)
        y = randint(0, world_height - 1)
        # change the tile at that spot on the world map to 1
        world_map[y][x] = 1

def make_player():
    player = Creature()
    player.xp = 0
    player.level = 0
    player.x = 300
    player.y = 150
    player.color = 1
    player.looks = "@"
    player.hp = 15
    player.maxhp = player.hp + 10
    player.speed = 10
    player.strength = 1
    player.name = "player"
    player.target = None
    player.mode = None
    player.inventory = []
    player.gold = 0
    return player

def make_scorpion(x,y):
    scorpion = Creature()
    scorpion.xp = 40
    scorpion.x = x
    scorpion.y = y
    scorpion.looks = "s"
    scorpion.color = 4
    scorpion.hp = 4
    scorpion.speed = 13
    scorpion.mode = "wander"
    scorpion.strength = 0
    scorpion.target = None
    scorpion.name = "Scorpio"
    return scorpion

def make_boulder(x, y):
    boulder = Creature()
    boulder.xp = 500
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
    goblin.xp = 25
    goblin.x = x
    goblin.y = y
    goblin.looks = "g"
    goblin.color = 3
    goblin.hp = 5
    goblin.speed = 11
    goblin.strength = 1
    goblin.target = None
    goblin.mode = "wander"
    goblin.name = "Gobbo"
    return goblin

def get_level_xp(level):
    if level == 0:
        return 50
    else:
        return get_level_xp(level - 1) + (level * 40)

def die(c, creatures, items):
    creatures.remove(c)
    item_roll = randint(1, 100)
    if item_roll < 50:
        amount = randint(1, 2)
        which_item = amount
        gold = Item(c.x, c.y, "$", "money", 4, amount)
        potion = Item(c.x, c.y, "8", "Bubbly dark potion", 2, 0)

        if which_item == 1:
            items.append(gold)
        if which_item == 2:
            items.append(potion)


def ord_to_number(inp):
    return inp - 48

def use_item(i, player):
    if i.name == "Bubbly dark potion":
        player.hp += 5
    elif i.name == "Crispy bright potion":
        player.hp -= 1000




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
    elif ord_to_number(inp) in list(range(10)): #player presses a number
        number_pressed = ord_to_number(inp)
        if number_pressed <= len(player.inventory):
            i = player.inventory.pop(number_pressed - 1)
            use_item(i, player)
    for c in creatures:
        if player.x == c.x and c.y == player.y and player != c:
            player.x = oldx
            player.y = oldy
            attack(player, c)
            # This code shouldn't be here
            # It really really shouldnt be here! it's causing enemies not to die
            # when hit by boulders
            # fill in the "die" function above
            if c.hp <= 0:
                player.xp += c.xp

                if player.xp > get_level_xp(player.level):
                    player.level += 1
                    # actually level up
                    player.maxhp += 5
                    player.strength += 1
                    player.speed += 1
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