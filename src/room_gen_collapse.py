# Room generation test implementation.
from enum import Enum
from random import shuffle, sample
from weighted_random import WeightedRandom
from typing import TypeAlias
from PIL import Image, ImageDraw
from dataclasses import dataclass

yx: TypeAlias = tuple[int, int]
Walls: TypeAlias = list[list[bool]]

WALL_LENGTH = 100
WALL_THICKNESS = 2
ROOM_MARGIN = 10

@dataclass
class Room:
    height: int
    width: int
    entrance_y: int
    exit_easy_y: int
    exit_hard_y: int
    walls_h: Walls
    walls_v: Walls

def create_grid(height: int, width: int, entrance_y: int, exit_easy_y: int, exit_hard_y: int) -> Room:
    # Fill all room with walls.
    walls_h = [ [ True for _ in range(width) ] for _ in range(height + 1) ]
    walls_v = [ [ True for _ in range(width + 1) ] for _ in range(height) ]

    # Clear out entrance/exit walls.
    walls_v[entrance_y][0] = False
    walls_v[exit_easy_y][width] = False
    walls_v[exit_hard_y][width] = False

    return Room(height, width, entrance_y, exit_easy_y, exit_hard_y, walls_h, walls_v)

class Direction(Enum):
    LEFT = 0, -1,
    UP = -1, 0,
    RIGHT = 0, 1,
    DOWN = 1, 0

def create_maze(room: Room):
    visited = [ [ False for _ in range(room.width) ] for _ in range(room.height) ]
    path = []
    st: list[tuple[int, int, Direction | None]] = [ (room.entrance_y, 0, None) ]

    while len(st) > 0:
        y, x, direction_from = st.pop()

        if visited[y][x]:
            continue

        visited[y][x] = True
        path.append((y, x, direction_from))

        shuffled_directions = [ d for d in Direction ]
        shuffle(shuffled_directions)
        for direction in shuffled_directions:
            dy, dx = direction.value
            ny = y + dy
            nx = x + dx
            if ny >= 0 and nx >= 0 and ny < room.height and nx < room.width:
                st.append((ny, nx, direction))

    # Clearing out the walls in the traced path.
    for y, x, direction in path:    
        if direction == None:
            continue
        elif direction == Direction.LEFT:
            room.walls_v[y][x + 1] = False
        elif direction == Direction.UP:
            room.walls_h[y + 1][x] = False
        elif direction == Direction.RIGHT:
            room.walls_v[y][x] = False
        else:
            room.walls_h[y][x] = False
            
def remove_random_walls(room: Room, emptiness: float):
    walls_h_n = (room.height - 1)*room.width
    walls_v_n = (room.width - 1)*room.height

    walls_h_to_remove_n = int(walls_h_n*emptiness)
    walls_v_to_remove_n = int(walls_v_n*emptiness)

    walls_h_to_remove_idxs = sample(range(walls_h_n), k=walls_h_to_remove_n)
    walls_v_to_remove_idxs = sample(range(walls_v_n), k=walls_v_to_remove_n)

    # Map to yx values and offset by 1 to not touch main walls.
    walls_h_to_remove_idxs = list(map(lambda idx: (idx // room.width + 1, idx % room.width), walls_h_to_remove_idxs))
    # For vertical walls the situation is a little bit more complex, 
    # since we need to skip a different number of walls for each row.
    walls_v_to_remove_idxs = list(map(lambda idx: (idx // (room.width - 1), idx % (room.width - 1) + 1), walls_v_to_remove_idxs))

    for y, x in walls_h_to_remove_idxs:
        room.walls_h[y][x] = False

    for y, x in walls_v_to_remove_idxs:
        room.walls_v[y][x] = False

def display_room(room: Room):
    im_height = 2*ROOM_MARGIN + room.height*WALL_LENGTH + WALL_THICKNESS
    im_width = 2*ROOM_MARGIN + room.width*WALL_LENGTH + WALL_THICKNESS
    with Image.new("RGB", size=(im_width, im_height), color=(255, 255, 255)) as im:
        im_draw = ImageDraw.Draw(im)

        # Render horizontal walls.
        for y1 in range(room.height + 1):
            for x1 in range(room.width):
                if not room.walls_h[y1][x1]:
                    continue
                # Top left corner.
                im_y1 = ROOM_MARGIN + y1*WALL_LENGTH
                im_x1 = ROOM_MARGIN + x1*WALL_LENGTH
                # Bottom right corner.
                im_y2 = im_y1 + WALL_THICKNESS
                im_x2 = im_x1 + WALL_LENGTH
                im_draw.rectangle(((im_x1, im_y1), (im_x2, im_y2)), fill=(0, 0, 0))

        # Render vertical walls.
        for y1 in range(room.height):
            for x1 in range(room.width + 1):
                if not room.walls_v[y1][x1]:
                    continue
                # Top left corner.
                im_y1 = ROOM_MARGIN + y1*WALL_LENGTH
                im_x1 = ROOM_MARGIN + x1*WALL_LENGTH
                # Bottom right corner.
                im_y2 = im_y1 + WALL_LENGTH
                im_x2 = im_x1 + WALL_THICKNESS
                im_draw.rectangle(((im_x1, im_y1), (im_x2, im_y2)), fill=(0, 0, 0))

        im.show()

if __name__ == "__main__":
    room = create_grid(15, 30, 7, 3, 11)
    create_maze(room)
    remove_random_walls(room, 0.95)
    display_room(room)
