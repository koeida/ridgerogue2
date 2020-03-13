import curses
from copy import copy

import gglobals
from gglobals import world_height


def initialize_colors():
    # initialize colors
    set_color(1, 800, 200, 150)
    set_color(3, 0, 900, 0)
    set_color(4, 1000, 1000, 0)

def set_color(color_number, r, g, b):
    curses.init_color(color_number, r, g, b)
    curses.init_pair(color_number, color_number, curses.COLOR_BLACK)

def draw_map(screen, tiles, world_map, middle_x, middle_y, window_width, window_height):
    end_x, end_y, start_x, start_y = get_window(middle_x, middle_y)
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            cur_tile_num = world_map[y][x]
            cur_tile = tiles[cur_tile_num]
            screen.addstr(y - start_y, x - start_x, cur_tile.tile, curses.color_pair(0))


def get_window(middle_x, middle_y):
    start_y = middle_y - int(gglobals.window_height / 2)
    start_x = middle_x - int(gglobals.window_width / 2)
    end_y = start_y + gglobals.window_height
    end_x = start_x + gglobals.window_width
    return end_x, end_y, start_x, start_y

def draw_inventory(inventory, screen):
    starty = 0
    screen.addstr (starty, gglobals.window_width + 1, "Inventory:", 0)
    for i in inventory:
        starty += 1
        display_str = " %d (%s): %s" % (starty, i.looks, i.name)
        screen.addstr(starty, gglobals.window_width, display_str, 0) #using item properties and starty
def draw_news(screen):
    if gglobals.news != []:
        n = 0

        n2 = copy(gglobals.news)
        n2.reverse()
        n2 = n2[:5]

        for x in n2:
            screen.addstr(gglobals.window_height + 2 + n, 0, x, curses.color_pair(0))
            n += 1

def draw_screen(creatures, player, screen, tiles, world_map, items):
    draw_map(screen, tiles, world_map, player.x, player.y, gglobals.window_width, gglobals.window_height)
    end_x, end_y, start_x, start_y = get_window(player.x, player.y)
    for c in creatures:
        draw_object(c, screen, start_x, start_y)
    for i in items:
        draw_object(i, screen, start_x, start_y)
    draw_news(screen)
    draw_inventory(player.inventory, screen)
    screen.addstr(gglobals.window_height, 0, "you have " + str(player.hp) + " health", curses.color_pair(1))
    screen.addstr(gglobals.window_height + 1, 0, "you have " + str(player.gold) + " gold", curses.color_pair(3))
    screen.refresh()


def draw_object(c, screen, start_x, start_y):
    cx = c.x - start_x
    cy = c.y - start_y
    if cx >= 0 and cx < gglobals.window_width and cy >= 0 and cy < gglobals.window_height:
        # do screen.addstr using the properties of each creature
        screen.addstr(cy, cx, c.looks, curses.color_pair(c.color))


