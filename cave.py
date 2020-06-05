from random import randint


def safe_query(x, y, m):
    try:
        return m[y][x]
    except:
        return None


def num_neighbors(x, y, cave, bacterea_tile):
    count = 0
    # Look at the squares north, south, east, and west of cave[y][x]
    # if the north square has a value of bacterea_tile, increase the count
    if safe_query(x, y - 1, cave) == bacterea_tile:
        count += 1
    if safe_query(x,y + 1, cave) == bacterea_tile:
        count += 1
    if safe_query(x - 1, y, cave) == bacterea_tile:
        count += 1
    if safe_query(x + 1, y, cave) == bacterea_tile:
        count += 1
    # and count how many of them are == bacterea_tile
    return count


def plop_down_diggers(num_diggers, cave, empty_tile):
    height = len(cave) - 1
    width = len(cave[0]) - 1
    # Pick num_diggers number of random coordinates
    for d in range(num_diggers):
        dx = randint(0, width)
        dy = randint(0, height)
        cave[dy][dx] = empty_tile
    # and set those coordinates to empty_tile


def check_cave_tile(x, y, cave, empty_tile, cave_tile, death_rate):
    # If we're looking at a cave tile, maybe dig it out
    current_tile = cave[y][x]
    if current_tile == cave_tile:
        ncount = num_neighbors(x, y, cave, empty_tile)
        birth_roll = randint(1,100)
        if ncount == 1 and birth_roll <= 1:
            cave[y][x] = empty_tile
        elif ncount == 2 and birth_roll <= 13:
            cave[y][x] = empty_tile
        elif ncount == 3 and birth_roll <= 20:
            cave[y][x] = empty_tile
        elif ncount == 4 and birth_roll <= 50:
            cave[y][x] = empty_tile

    # Set up percent chance that cave tile becomes empty tile
        # based on number of neighbors

        # Figure out if this cave tile should be hollowed out based on number of neighbors

    # If we're looking at an empty tile, maybe it "dies" and reverts to a cave tile
    if current_tile == empty_tile:
        # Pick a number between 1 and 100
        maybe_death = randint(1, 100)
        # If that number is less than or equal to the death rate, die
        if maybe_death <= death_rate:
            cave[y][x] = cave_tile


def grow_cave(width, height, num_diggers, num_cycles, death_rate=1, cave_tile="#", empty_tile="."):
    # Create full cave
    cave = [[cave_tile for x in range(width)] for y in range(height)]

    # Plop down diggers
    plop_down_diggers(num_diggers, cave, empty_tile)

    # Run the set number of cycles
    for cycle_num in range(num_cycles):
        # Every cycle, check every tile to see whether it becomes empty or full
        for y in range(height):
            for x in range(width):
                check_cave_tile(x, y, cave, empty_tile, cave_tile, death_rate)

    return cave


cave = grow_cave(80, 300, 1750, 100, death_rate=2)
for row in cave:
    row = "".join(row)
    print(row)
