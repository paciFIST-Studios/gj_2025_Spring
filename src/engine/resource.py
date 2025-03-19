import json
import os

from pygame import (mixer as pygame_mixer,
                    font as pygame_font,
                    image as pygame_image,
                    error as pygame_error)

# objects to load


IMAGES_TO_LOAD = [
    # player stances
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_stand.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_duck.png' ,
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_front.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_hurt.png' ,
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_jump.png' ,

    # player walk animation
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_walk/PNG/p1_walk01.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_walk/PNG/p1_walk02.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_walk/PNG/p1_walk03.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_walk/PNG/p1_walk04.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_walk/PNG/p1_walk05.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_walk/PNG/p1_walk06.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_walk/PNG/p1_walk07.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_walk/PNG/p1_walk08.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_walk/PNG/p1_walk09.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_walk/PNG/p1_walk10.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_walk/PNG/p1_walk11.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_walk/PNG/p1_walk12.png',

    # cactus
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/cactus.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Tiles/dirtHalf.png',

    # things the cactus might be attached to
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Tiles/bridge.png',
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Tiles/castleHalf.png',
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Tiles/grassHalf.png',
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/cloud1.png',
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/bush.png',

    # # plant
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/plant.png',

    # gems
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/gemBlue.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/gemYellow.png',

    # # star
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/star.png',
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/rock.png',

    # # switch
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/switchLeft.png',
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/switchMid.png',
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/switchRight.png',

    # locks
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Tiles/lock_blue.png',
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Tiles/lock_green.png',
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Tiles/lock_red.png',
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Tiles/lock_yellow.png',

    # keys
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/keyBlue.png',
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/keyGreen.png',
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/keyRed.png',
    # '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/keyYellow.png',

    # buttons
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/buttonYellow.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/buttonYellow_pressed.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/buttonBlue.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/buttonBlue_pressed.png',

    # blocks
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Tiles/castleCenter_rounded.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Tiles/brickWall.png',

]

AUDIO_TO_LOAD = [
    '/home/ellie/git/gj_2025_Spring/resources/GUI_Sound_Effects_by_Lokif/misc_menu_2.mp3',
    '/home/ellie/git/gj_2025_Spring/resources/GUI_Sound_Effects_by_Lokif/misc_menu_4.mp3',
    '/home/ellie/git/gj_2025_Spring/resources/GUI_Sound_Effects_by_Lokif/sharp_echo.mp3',
    '/home/ellie/git/gj_2025_Spring/resources/krank_sounds/unlink.mp3',
    '/home/ellie/git/gj_2025_Spring/resources/Luke.RUSTLTD/coin_sounds/coin7.mp3',
    '/home/ellie/git/gj_2025_Spring/resources/Luke.RUSTLTD/coin_sounds/coin10.mp3',

    # player touches cactus
    '/home/ellie/git/gj_2025_Spring/resources/The Essential Retro Video Game Sound Effects Collection [512 sounds] By Juhani Junkala/General Sounds/Impacts/sfx_sounds_impact7.wav'

    # player's streak size increases by a category
    '/home/ellie/git/gj_2025_Spring/resources/The Essential Retro Video Game Sound Effects Collection [512 sounds] By Juhani Junkala/General Sounds/Positive Sounds/sfx_sounds_powerup9.wav'
    '/home/ellie/git/gj_2025_Spring/resources/The Essential Retro Video Game Sound Effects Collection [512 sounds] By Juhani Junkala/General Sounds/Positive Sounds/sfx_sounds_powerup14.wav'

]

# NOTE: to have different font sizes, you need to pull them in at that size
FONTS_TO_LOAD = [
    ('lcd_big', 70, '/home/ellie/git/gj_2025_Spring/resources/LCD Mono/lcd_lcd_mono/LCDMonoWinTT/LCDM2N__.TTF'),
    ('lcd', 40, '/home/ellie/git/gj_2025_Spring/resources/LCD Mono/lcd_lcd_mono/LCDMonoWinTT/LCDM2N__.TTF'),
    ('lcd_small', 30, '/home/ellie/git/gj_2025_Spring/resources/LCD Mono/lcd_lcd_mono/LCDMonoWinTT/LCDM2N__.TTF'),
    ('dos', 24, '/home/ellie/git/gj_2025_Spring/resources/good_old_dos_font/GoodOldDOS.ttf'),
    ('estrogen', 60, '/home/ellie/git/gj_2025_Spring/resources/estrogen_font/estrogen/ESTROG__.ttf'),
    ('love', 24, '/home/ellie/git/gj_2025_Spring/resources/pil_love/pil_love.ttf'),
    ('open_dyslexic', 18, '/home/ellie/git/gj_2025_Spring/resources/open_dyslexic/OpenDyslexicAlta-Regular.otf')
]

DEFAULT_INPUT_MAPPING = '/home/ellie/git/gj_2025_Spring/resources/default_input_mappings.json'


# loading functions ----------------------------------------------------------------------------------------------------


def load_text_file(path: str):
    if os.path.isfile(path):
        with open(path, 'r') as infile:
            return infile.read()

def load_json(path):
    data = load_text_file(path)
    if data:
        return json.loads(data)

def write_text_file(path: str, data) -> bool:
    with open(path, 'w') as outfile:
        outfile.write(data)
    return True

def write_json(path: str, obj) -> bool:
    jstr = json.dumps(obj)
    return write_text_file(path, jstr)

def load_image(path: str):
    if os.path.isfile(path):
        try:
            # note, calling convert, or convert_alpha here is crucial, b/c pygame will re-order the internal
            # color channels of the image, to match the running machine's hardware
            return pygame_image.load(path).convert_alpha()
        except pygame_error as err:
            print(f'Could not load image="{path}"\n{err}')

def load_sound(path: str):
    if pygame_mixer and os.path.isfile(path):
        try:
            return pygame_mixer.Sound(path)
        except pygame_error as err:
            print(f'Cannot load sound="{path}"\n{err}')

def load_font(path: str, size: int):
    if os.path.isfile(path):
        try:
            return pygame_font.Font(path, size)
        except pygame_error as err:
            print(f'Cannot load font="{path}"\n{err}')
