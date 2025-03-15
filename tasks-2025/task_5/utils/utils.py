from enum import IntEnum

def constructor(self: object) -> None:
    self.foo = "bar"

def outside_function(self: object) -> None:
    print(self.foo)

def add(a: int, b: int) -> int:
    return a + b

class FieldType(IntEnum):
    OCCUPIED_PLAYER1 = 0b01000000
    OCCUPIED_PLAYER2 = 0b10000000

    SPACE = 0b00000000
    PLANET_NO_RESOURCES = 0b00000001
    ASTEROID = 0b00000010
    ROUGH_LAND = 0b00000011
    IONIZED_FIELD = 0b00000100

    RESOURCE_1 = 0b00001001  # 9

    RESOURCE_2 = 0b00010001  # 17

    RESOURCE_3 = 0b00011001  # 25

    RESOURCE_4 = 0b00111001  # 57

    PLANET_PLAYER_1 = PLANET_NO_RESOURCES | OCCUPIED_PLAYER1  # 65
    PLANET_PLAYER_2 = PLANET_NO_RESOURCES | OCCUPIED_PLAYER2  # 129

    PLANET_RESOURCE_1_PLAYER1 = RESOURCE_1 | OCCUPIED_PLAYER1
    PLANET_RESOURCE_2_PLAYER1 = RESOURCE_2 | OCCUPIED_PLAYER1
    PLANET_RESOURCE_3_PLAYER1 = RESOURCE_3 | OCCUPIED_PLAYER1
    PLANET_RESOURCE_4_PLAYER1 = RESOURCE_4 | OCCUPIED_PLAYER1

    PLANET_RESOURCE_1_PLAYER2 = RESOURCE_1 | OCCUPIED_PLAYER2  # 137
    PLANET_RESOURCE_2_PLAYER2 = RESOURCE_2 | OCCUPIED_PLAYER2  # 137
    PLANET_RESOURCE_3_PLAYER2 = RESOURCE_3 | OCCUPIED_PLAYER2  # 153
    PLANET_RESOURCE_4_PLAYER2 = RESOURCE_4 | OCCUPIED_PLAYER2

    UNDEFINED_PLAYER_1 = 0b01000011  # 67
    UNDEFINED_PLAYER_2 = 0b10000011  # 131

    def is_occupied(self):
        return (self & FieldType.OCCUPIED_PLAYER1) or (self & FieldType.OCCUPIED_PLAYER2)

    def is_planet(self) -> bool:
        return (self & 0b00000001) == FieldType.PLANET_NO_RESOURCES

    @classmethod
    def decode_tile(cls, value: int) -> 'FieldType':
        try:
            return cls(value)
        except ValueError:
            return None

