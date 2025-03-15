import pygame

from pygame import Color, BLEND_MULT

from octospace.envs.game_config import (SHIP_SIZE, SIDE_SHIP_SIZE, TILE_SIZE, PLAYER_ICON_SIZE, WINDOW_SIZE,
                         EFFECT_IONIZED_FIELD_SIZE, RF_MARKER_SIZE, RF_ICON_SIZE, RF_BAR_SIZE, GUI_SIZE, BORDER_WIDTH,
                         PLAYER_ICON_TEAM_NAME_SIZE, FLAG_SIZE, OCCUPATION_BAR_SIZE, EFFECT_DEATH_SIZE,
                         EFFECT_FIRING_SIZE, EFFECT_HEALING_SIZE, EFFECT_CAPTURE_SIZE, EFFECT_SPACE_JUMP_SIZE,
                         ASTEROID_SIZE)


BACKGROUND = pygame.image.load('assets/background.jpg')
BORDER = pygame.transform.scale(pygame.image.load('assets/border_long.png'), (WINDOW_SIZE + 2*BORDER_WIDTH, WINDOW_SIZE))
BORDER_SCORE = pygame.transform.scale(pygame.image.load('assets/scoreboard.png'), (WINDOW_SIZE + 2*BORDER_WIDTH - 50, WINDOW_SIZE - 300))
LAND = {
    i: pygame.transform.scale(pygame.image.load(f'assets/planets/land_{i}.png'), size=(TILE_SIZE, TILE_SIZE))
    for i in range(13)
}
ASTEROIDS = {
    i: pygame.transform.scale(pygame.image.load(f'assets/asteroids/asteroid_{i}.png'), size=(ASTEROID_SIZE, ASTEROID_SIZE))
    for i in range(12)
}

PLAYER_ICON = pygame.transform.scale(pygame.image.load('assets/tentacle_white_ring.png'), size=(PLAYER_ICON_TEAM_NAME_SIZE, PLAYER_ICON_TEAM_NAME_SIZE))
OCCUPATION_FLAG = pygame.transform.scale(pygame.image.load('assets/flag_small.png'), size=(FLAG_SIZE, FLAG_SIZE))
OCCUPATION_FLAG_CROSSED = pygame.transform.scale(pygame.image.load('assets/flag_small_crossed.png'), size=(FLAG_SIZE, FLAG_SIZE))

ROUGH_TERRAIN = {
    i: pygame.transform.rotate(pygame.transform.scale(pygame.image.load('assets/planets/rough_terrain.png'), size=(TILE_SIZE, TILE_SIZE)), angle=i*90)
    for i in range(4)
}
ROUGH_TERRAIN_FLAG = pygame.transform.scale(pygame.image.load('assets/planets/rough_terrain_flag.png'), size=(TILE_SIZE, TILE_SIZE))

ROUGH_TERRAIN_CORNER = {
    i: pygame.transform.rotate(
        pygame.transform.scale(pygame.image.load('assets/planets/rough_terrain_corner.png'), size=(TILE_SIZE, TILE_SIZE)),
        angle=i * 90)
    for i in range(4)
}

RESOURCE_FIELDS_MARKERS = {
    i: pygame.transform.scale(pygame.image.load(f'assets/rf_icons/rf_{i}.png'), size=(RF_MARKER_SIZE, RF_MARKER_SIZE)) for i in range(4)
}

RESOURCE_FIELDS_ICONS = {
    i: pygame.transform.scale(pygame.image.load(f'assets/rf_icons/rf_icon_{i}.png'), size=(RF_ICON_SIZE, RF_ICON_SIZE)) for i in range(4)
}

RESOURCE_FIELDS_BARS = [
    {i: pygame.transform.scale(pygame.image.load(f'assets/rf_bars/bar_{color}_{i}.png'), size=(RF_BAR_SIZE, RF_BAR_SIZE//5)) for i in range(10)}
    for color in ['gray', 'green', 'brown', 'blue']
]

BAR_EMPTY = pygame.transform.scale(pygame.image.load('assets/rf_bars/bar_empty.png'), size=(OCCUPATION_BAR_SIZE, OCCUPATION_BAR_SIZE//5))

IONIZED_FIELDS = {
    i: pygame.transform.scale(pygame.image.load(f'assets/effects/ionized_field_animation/ionized_field_blue_{i}.png'),
                              size=(EFFECT_IONIZED_FIELD_SIZE, EFFECT_IONIZED_FIELD_SIZE))
    for i in range(12)
}

DEATH_EFFECT_ANIMATION = {
    i: pygame.transform.scale(pygame.image.load(f'assets/effects/death_animation/death_animation_{i}.png'),
                              size=(EFFECT_DEATH_SIZE, EFFECT_DEATH_SIZE))
    for i in range(15)
}

HEALING_EFFECT_ANIMATION = {
    i: pygame.transform.scale(pygame.image.load(f'assets/effects/healing_animation/healing_animation_{i}.png'),
                              size=(EFFECT_HEALING_SIZE, EFFECT_HEALING_SIZE))
    for i in range(15)
}

FIRING_EFFECT_ANIMATION = {
    direction: {
        i: pygame.transform.rotate(pygame.transform.scale(pygame.image.load(f'assets/effects/firing_animation/firing_animation_{i}.png'),
                              size=(EFFECT_FIRING_SIZE, EFFECT_FIRING_SIZE)), angle=65-90*direction)
        for i in range(5)
    } for direction in range(4)
}

CAPTURE_EFFECT_ANIMATION = {
    i: pygame.transform.scale(pygame.image.load(f'assets/effects/capture_animation/capture_animation_{i}.png'),
                              size=(EFFECT_CAPTURE_SIZE, EFFECT_CAPTURE_SIZE))
    for i in range(12)
}

SPACE_JUMP_EFFECT_ANIMATION = {
    i: pygame.transform.scale(pygame.image.load(f'assets/effects/space_jump/space_jump_{i}.png'),
                              size=(EFFECT_SPACE_JUMP_SIZE, EFFECT_SPACE_JUMP_SIZE))
    for i in range(9)
}

TEAM_COLORS = {
    0: Color(233, 47, 137, 255),
    1: Color("aliceblue"),
    2: Color("aqua"),
    3: Color("antiquewhite"),
    4: Color("red"),
    5: Color("blue"),
    6: Color("brown"),
    7: Color("cadetblue"),
    8: Color("cornflowerblue"),
    9: Color("crimson"),
    10: Color("darkblue"),
    11: Color("darkgoldenrod"),
    12: Color("gold"),
    13: Color("cyan"),
    14: Color("darkmagenta"),
    15: Color("darkolivegreen1"),
    16: Color("darkorchid"),
    17: Color("darksalmon"),
    18: Color("darkseagreen"),
    19: Color("deeppink"),
    20: Color("deepskyblue"),
    21: Color("fuchsia"),
    22: Color("forestgreen"),
    23: Color("ghostwhite"),
    24: Color("green"),
    25: Color("greenyellow"),
    26: Color("grey"),
    27: Color("hotpink"),
    28: Color("khaki"),
    29: Color("lightpink"),
    30: Color("lightseagreen"),
    31: Color("lightsteelblue1"),
    32: Color("lightyellow4"),
    33: Color("mediumaquamarine"),
    34: Color("mediumspringgreen"),
    35: Color("mintcream"),
    36: Color("navy"),
    37: Color("orange"),
    38: Color("palegreen"),
    39: Color("palegreen4"),
    40: Color("powderblue"),
    41: Color("purple"),
    42: Color("rosybrown"),
    43: Color("seagreen"),
    44: Color("skyblue"),
    45: Color("tan"),
    46: Color("teal"),
    47: Color("violet"),
    48: Color("wheat"),
    49: Color("yellow"),
    50: Color("violetred4"),
}

TEAM_ICONS = {
    team_id: pygame.transform.scale(
        pygame.image.load(f'assets/player_icons/octopus_{team_id}.png'), size=(PLAYER_ICON_SIZE, PLAYER_ICON_SIZE)
    ) for team_id in range(51)
}

"""
Different images are going to be rendered based on which side is the ship currently facing.
0 - right
1 - down
2 - left
3 - up
"""
SHIP_ORIENTATIONS_1 = {}
SHIP_ORIENTATIONS_2 = {}

SHIP_ORIENTATIONS_MAP = {
    0: 'side',
    1: 'front',
    2: 'side',
    3: 'back'
}


def generate_players_assets(
    player_1_id: int,
    player_2_id: int
):
    for i in range(4):
        ship_img_1 = pygame.image.load(f'assets/battleship_{SHIP_ORIENTATIONS_MAP[i]}.png')
        if i == 2:
            ship_img_1 = pygame.transform.flip(ship_img_1, flip_x=True, flip_y=False)
        if i in [0, 2]:
            ship_img_1 = pygame.transform.scale(ship_img_1, size=(SIDE_SHIP_SIZE, SIDE_SHIP_SIZE))
        else:
            ship_img_1 = pygame.transform.scale(ship_img_1, size=(SHIP_SIZE, SHIP_SIZE))
        ship_img_2 = ship_img_1.copy()

        ship_img_1.fill(TEAM_COLORS[player_1_id], special_flags=BLEND_MULT)
        ship_img_2.fill(TEAM_COLORS[player_2_id], special_flags=BLEND_MULT)

        SHIP_ORIENTATIONS_1[i] = ship_img_1
        SHIP_ORIENTATIONS_2[i] = ship_img_2


