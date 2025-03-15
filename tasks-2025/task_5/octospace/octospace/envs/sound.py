import numpy as np
import pygame


TRACKS = [
    'track_1_neon_gaming.mp3',
    'track_2_the_console_of_my_dreams.mp3',
    'track_3_the_return_of_the_8_bit_era.mp3',
    'track_4_8_bit.mp3',
    'track_5_8_bit_air_fight.mp3',
    'track_6_8_bit_arcade_mode.mp3',
    'track_7_8_bit_game.mp3',
    'track_8_a_video_game.mp3',
    'track_9_level_iii.mp3',
    'track_10_retro_8bit_happy_adventure_videogame_music.mp3'
]

current_track_id = 0


def get_new_track():
    next_track_id = np.random.randint(0, len(TRACKS))
    while next_track_id == current_track_id:
        next_track_id = np.random.randint(0, len(TRACKS))

    pygame.mixer.music.load(f'assets/sounds/{TRACKS[next_track_id]}')
    pygame.mixer.music.play()


def setup_music_loop(volume: float = 0.25):
    pygame.mixer.init()
    pygame.mixer.music.set_volume(volume)
    get_new_track()


def play_shoot_sound(volume: float):
    shoot_sound = pygame.mixer.Sound('assets/sounds/shot_1.wav')
    shoot_sound.set_volume(volume*2.0)
    pygame.mixer.Channel(1).play(shoot_sound)


def play_space_jump_sound(volume: float):
    space_jump_sound = pygame.mixer.Sound('assets/sounds/space_jump.mp3')
    space_jump_sound.set_volume(volume * 2.0)
    pygame.mixer.Channel(3).play(space_jump_sound)


def play_capture_sound(volume: float):
    capture_sound = pygame.mixer.Sound('assets/sounds/capture.mp3')
    capture_sound.set_volume(volume * 0.5)
    pygame.mixer.Channel(4).play(capture_sound)


def play_ship_explosion_sound(volume: float):
    sound_file = pygame.mixer.Sound('assets/sounds/ship_explosion.ogg')
    sound_file.set_volume(volume * 0.75)
    pygame.mixer.Channel(2).play(sound_file)