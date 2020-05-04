import curses
from random import randint, choice
from math import sqrt
import gglobals
from display import initialize_colors, draw_screen
from gglobals import world_width, world_height, KEY_Q

MAX_HEALTH_TIMER = 13

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
    else:
        # deal with this next time: boulders aren't hitting creatures (other than player)
        # or rather don't seem to be doing damage to them.
        if result == "hit":
            stat = "cspeed(%d) + roll(%d) >= tspeed(%d) + roll(%d)" % (c.speed, player_roll, t.speed, monster_roll)
            gglobals.news.append(stat)
        else:
            stat = "cspeed(%d) + roll(%d) < tspeed(%d) + roll(%d)" % (c.speed, player_roll, t.speed, monster_roll)
            gglobals.news.append(stat)

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

    creatures, player, tiles, world_map, items = initialize_world()

    gglobals.news.append("Welcome to RidgeRogue II")

    while (inp != KEY_Q):  # Quit game if player presses "q"
        screen.clear()

        limit_hp(player)

        health_timer -= 1
        if health_timer == 0:
            health_timer = MAX_HEALTH_TIMER
            player.hp += 1
        spawn_roll = randint(1, 4)
        if spawn_roll == 3 and len(creatures) <= 80:
            spawn_monster(creatures, player, world_map, tiles)

        b_roll = randint(1, 10)
        if b_roll < 3:
            wobble = randint(-5, 5)
            b = make_boulder(player.x + wobble, player.y - 30)
            creatures.append(b)

        keyboard_input(creatures, inp, player, world_map, tiles, items)

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


def initialize_world():
    player = make_player()
    creatures = [player]
    items = []
    world_map = [[0 for x in range(world_width)] for y in range(world_height)]
    tiles = {0: Tile(".", True),
             1: Tile("#", False)}
    make_path(world_map)
    make_random_rocks(world_map)

    for x in range(0,len(world_map[0])):
        if world_map[player.y][x] == 0:
            player.x = x
    health_potion = Item(player.x - 1, player.y, "8", "Bubbly dark potion", 4, 0)
    items.append(health_potion)
    return creatures, player, tiles, world_map, items


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
        i = player.inventory.pop(number_pressed)
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