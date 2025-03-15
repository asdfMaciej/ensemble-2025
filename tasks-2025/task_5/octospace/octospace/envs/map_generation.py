import numpy as np

from octospace.envs.game_config import (PLANETS_DIAMETER, PLANETS_OFFSET, PLANETS_DISTANCE,
                         RF_ID_TO_CODING, RF_COORDS, FRAC_OF_ASTEROID_AREA, FRAC_OF_IONIZED_AREA, BOARD_SIZE,
                         PLAYER_1_ORIGIN, PLAYER_2_ORIGIN, N_PLANETS)
from octospace.envs.map_assets import (IONIZED_FIELDS, LAND, ASTEROIDS)
from octospace.envs.schemes import (STARTING_PLANET_SCHEME, EMPTY_PLANET_SCHEME, ASTEROID_ID_TO_SCHEME, ASTEROID_AREA, PLANET_MASK)
from scipy.spatial.distance import cdist
from octospace.envs.utils import NoSpaceOnMapException


def _generate_map():
    """
    Function generates a new map.

    :return: np.ndarray of shape (BOARD_SIZE, BOARD_SIZE)
    """
    game_map = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)

    # Generate starting planets
    game_map[PLANETS_OFFSET:PLANETS_OFFSET + PLANETS_DIAMETER,
    PLANETS_OFFSET:PLANETS_OFFSET + PLANETS_DIAMETER] = STARTING_PLANET_SCHEME

    game_map[BOARD_SIZE - (PLANETS_OFFSET + PLANETS_DIAMETER): BOARD_SIZE - PLANETS_OFFSET,
    BOARD_SIZE - (PLANETS_OFFSET + PLANETS_DIAMETER): BOARD_SIZE - PLANETS_OFFSET] = STARTING_PLANET_SCHEME

    centers = [PLAYER_1_ORIGIN, PLAYER_2_ORIGIN]

    # Generate unoccupied planets
    for _ in range(N_PLANETS):
        new_planet_center = np.random.randint(PLANETS_OFFSET, BOARD_SIZE - PLANETS_OFFSET, size=2, dtype=int)

        if len(centers) == 0:
            centers.append(new_planet_center)
            continue

        intra_dist = np.min(cdist([new_planet_center], centers))
        failed_attempts = 0
        while intra_dist <= PLANETS_DISTANCE:
            if failed_attempts >= 1000:
                raise NoSpaceOnMapException("There's no space to place that many planets on the map")

            new_planet_center = np.random.randint(PLANETS_OFFSET, BOARD_SIZE - PLANETS_OFFSET, size=2, dtype=int)
            intra_dist = np.min(cdist([new_planet_center], centers))
            failed_attempts += 1
        centers.append(new_planet_center)

    # Add base planet occupation
    _add_base_planet_occupation(game_map=game_map, centers=centers)

    # Delete the points for starting planets
    centers = np.array(centers[2:], dtype=int)

    for planet_center in centers:
        left_upper = (planet_center[0] - 4, planet_center[1] - 4)
        game_map[left_upper[0]:left_upper[0] + PLANETS_DIAMETER, left_upper[1]:left_upper[1] + PLANETS_DIAMETER] = (
            _generate_planet())

    # Generate asteroids
    area_left = int(BOARD_SIZE ** 2 * FRAC_OF_ASTEROID_AREA)
    max_asteroid_area = np.max(list(ASTEROID_AREA.values()))
    while area_left >= max_asteroid_area:
        asteroid_id = np.random.randint(0, len(ASTEROID_AREA.keys()), size=1, dtype=int)[0]
        asteroid_scheme = ASTEROID_ID_TO_SCHEME[asteroid_id]
        left_upper = (np.random.randint(0, BOARD_SIZE - asteroid_scheme.shape[0], size=1, dtype=int)[0],
                      np.random.randint(0, BOARD_SIZE - asteroid_scheme.shape[1], size=1, dtype=int)[0])

        failed_attempts = 0
        while np.sum(asteroid_scheme * game_map[left_upper[0]:left_upper[0] + asteroid_scheme.shape[0],
                                       left_upper[1]:left_upper[1] + asteroid_scheme.shape[1]]) != 0:
            if failed_attempts >= 1000:
                raise NoSpaceOnMapException("There's no space to place next asteroid field")
            left_upper = (np.random.randint(0, BOARD_SIZE - asteroid_scheme.shape[0], size=1, dtype=int)[0],
                          np.random.randint(0, BOARD_SIZE - asteroid_scheme.shape[1], size=1, dtype=int)[0])
            failed_attempts += 1

        game_map[left_upper[0]:left_upper[0] + asteroid_scheme.shape[0],
        left_upper[1]:left_upper[1] + asteroid_scheme.shape[1]] += asteroid_scheme

        area_left -= ASTEROID_AREA[asteroid_id]

    # Generate ionized fields (speed boost for ships)
    n_ionized_fields = int(BOARD_SIZE ** 2 * FRAC_OF_IONIZED_AREA)
    ionized_field_id = {}
    failed_attempts = 0
    while n_ionized_fields > 0:
        if failed_attempts >= 10000:
            raise NoSpaceOnMapException("There's no space to place next ionized field")

        field_position = np.random.randint(0, BOARD_SIZE, size=2, dtype=int)
        failed_attempts += 1

        if not game_map[field_position[0], field_position[1]]:
            failed_attempts = 0
            game_map[field_position[0], field_position[1]] = 4
            ionized_field_id[(field_position[0], field_position[1])] = np.random.randint(0, len(IONIZED_FIELDS.keys()) - 1)
            n_ionized_fields -= 1

    return game_map, centers, ionized_field_id


def _generate_planet():
    """
    Function generates a 9x9 scheme of a new planet, with random ratio of resource fields.
    There are in total 16 resource fields on a planet, and there needs to be at least 1 of each field.

    :return: np.ndarray with shape (9, 9)
    """
    resource_fields = []
    fields_left = 16
    for i in range(3):
        resource_fields.append(np.random.randint(1, fields_left - (3 - i)))
        fields_left -= resource_fields[-1]
    resource_fields.append(fields_left)

    planet_map = EMPTY_PLANET_SCHEME.copy()
    rf_id = 0
    for rf in RF_COORDS:
        planet_map[rf] = RF_ID_TO_CODING[rf_id]
        resource_fields[rf_id] -= 1
        if resource_fields[rf_id] == 0:
            rf_id += 1

    return planet_map


def _add_base_planet_occupation(game_map: np.ndarray, centers:list):
    map_mask = np.zeros((BOARD_SIZE, BOARD_SIZE))
    map_mask[centers[0][0] - 4: centers[0][0] + 5, centers[0][1] - 4: centers[0][1] + 5] = PLANET_MASK
    game_map[centers[0][0] - 4: centers[0][0] + 5, centers[0][1] - 4: centers[0][1] + 5] |= 64
    map_mask = np.zeros((BOARD_SIZE, BOARD_SIZE))
    map_mask[centers[1][0] - 4: centers[1][0] + 5, centers[1][1] - 4: centers[1][1] + 5] = PLANET_MASK
    game_map[centers[1][0] - 4: centers[1][0] + 5, centers[1][1] - 4: centers[1][1] + 5] |= 128


def _generate_state_map(game_map: np.ndarray):
    state_id_map = np.zeros(shape=game_map.shape)
    land_mask = game_map & 3 == 1
    land_non_zero = np.count_nonzero(land_mask)
    land_ids = np.random.randint(0, len(LAND.keys()), land_non_zero)
    state_id_map[land_mask] = land_ids

    asteroid_mask = game_map & 3 == 2
    asteroid_non_zero = np.count_nonzero(asteroid_mask)
    asteroid_ids = np.random.randint(0, len(ASTEROIDS.keys()), asteroid_non_zero)
    state_id_map[asteroid_mask] = asteroid_ids

    return state_id_map


# Sets 2 first bits of every map tile to 0
def _reset_planets_occupation(game_map: np.ndarray):
    game_map &= 63