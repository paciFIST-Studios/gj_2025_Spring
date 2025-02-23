import json
import os

from pygame import (mixer as pygame_mixer,
                    font as pygame_font,
                    image as pygame_image,
                    error as pygame_error)

# objects to load


IMAGES_TO_LOAD = [
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_stand.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/gemBlue.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/gemYellow.png',
    '/home/ellie/git/gj_2025_Spring/resources/illegal.png',
]

AUDIO_TO_LOAD = [
    '/home/ellie/git/gj_2025_Spring/resources/GUI_Sound_Effects_by_Lokif/misc_menu_2.mp3',
    '/home/ellie/git/gj_2025_Spring/resources/GUI_Sound_Effects_by_Lokif/misc_menu_4.mp3',
    '/home/ellie/git/gj_2025_Spring/resources/GUI_Sound_Effects_by_Lokif/sharp_echo.mp3',
    '/home/ellie/git/gj_2025_Spring/resources/krank_sounds/unlink.mp3',
    '/home/ellie/git/gj_2025_Spring/resources/Luke.RUSTLTD/coin_sounds/coin7.mp3',
    '/home/ellie/git/gj_2025_Spring/resources/Luke.RUSTLTD/coin_sounds/coin10.mp3',
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


# loading functions ----------------------------------------------------------------------------------------------------


def load_text_file(path):
    if os.path.isfile(path):
        try:
            with open(path, 'r') as infile:
                return infile.read()
        except Exception as ex:
            print(f'Could not load text file="{path}"\n{ex}')
    return None

def load_json(path):
    data = load_text_file(path)
    if data:
        try:
            return json.loads(data)
        except Exception as ex:
            print(f'Could not load json="{path}"\n{ex}')
    return None

def write_text_file(path, data):
    try:
        with open(path, 'w') as outfile:
            outfile.write(data)
    except Exception as ex:
        print(f'Could not write file="{path}"\n{ex}')

def write_json(path, obj):
    jstr = json.dumps(obj)
    write_text_file(path, jstr)

def load_image(path):
    if os.path.isfile(path):
        try:
            # note, calling convert, or convert_alpha here is crucial, b/c pygame will re-order the internal
            # color channels of the image, to match the running machine's hardware
            return pygame_image.load(path).convert_alpha()
        except pygame_error as err:
            print(f'Could not load image="{path}"\n{err}')
    return None

def load_sound(path):
    if pygame_mixer and os.path.isfile(path):
        try:
            return pygame_mixer.Sound(path)
        except pygame_error as err:
            print(f'Cannot load sound="{path}"\n{err}')
    return None

def load_font(path, size):
    if os.path.isfile(path):
        try:
            return pygame_font.Font(path, size)
        except pygame_error as err:
            print(f'Cannot load font="{path}"\n{err}')

