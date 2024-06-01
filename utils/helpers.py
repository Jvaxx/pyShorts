from pathlib import Path
from typing import Dict, Any, List
from PIL import ImageFont

background_standard_options: Dict[str, Any] = {
    'name_y_position': 290,
    'name_font': ImageFont.truetype(font='utils/fonts/OpenSans-Regular.ttf', size=35),
    'avatar_size': (180, 180),
    'avatar_position': (450, 100),
    'time_position': (115, 85),
    'time_font': ImageFont.truetype(font='utils/fonts/OpenSans-Bold.ttf', size=45),
    'message_font': ImageFont.truetype(font='utils/fonts/OpenSans-Regular.ttf', size=45),
    'message_max_width': 600,
    'message_x_padding': 30,
    'message_x_margin': 20,
    'message_y_padding': 30,
    'message_y_margin': 20,
    'message_radius': 50,
    'message_background_color_sending': '#0080FF',
    'message_background_color_receiving': '#E0DEE6',
    'message_first_y': 354,
    'message_area_size': (1080, 1566),
    'background_path': Path('Ressources/base sms iphone.png'),
    'avatar_path': Path('Ressources/profile default.png'),
    'intro_background_directory': 'Ressources/intro backgrounds/',
    'intro_font': ImageFont.truetype(font='utils/fonts/OpenSans-Bold.ttf', size=90),
    'intro_text_background_padding': 10,
    'intro_text_background_radius': 20
}


def format_text_box(text: str, max_width: int, font: ImageFont.ImageFont) -> str:
    """
    Format a given text to fit within the max width by adding returns to line where needed

    :param font: the font to use
    :type font: class: `ImageFont.ImageFont`
    :param text: the text to format
    :type text: str
    :param max_width: the maximum width of the resulting text (the result can be thinner)
    :type max_width: int
    :return: str: The formatted text compatible with the `maw_width` parameter
    """

    text_list = text.split()
    nb_words = len(text_list)
    last_words = [0]  # List containing the positions of last words of different lines

    nw = 0
    nl = 0
    while nw < nb_words:
        length = get_text_size(text_list[last_words[nl]:nw+1], font)
        # print(length, text_list[last_words[nl]:nw+1])
        if length > max_width:
            last_words.append(nw)
            # print(last_words)
            nl += 1
        nw += 1

    # print(last_words)

    # print(text_list)
    for i in range(len(last_words)):
        if i == 0:
            pass
        else:
            text_list[last_words[i]-1] = text_list[last_words[i]-1] + '\n'

    # print(text_list)
    res = ''
    for i, word in enumerate(text_list):
        res += word
        if i < len(text_list) - 1 and i+1 not in last_words:
            res += ' '
    return res


def get_text_size(text_list: List[str], font: ImageFont.ImageFont) -> int:
    """
    Calculate the length in pixels of a list of words

    :param font: the font used to calculate the length
    :type font: class: `ImageFont.ImageFont`
    :param text_list: the list of strings to handle
    :type text_list: List[str]
    :return: length in pixels of the given list. Type: int
    """

    x = 0
    for word in text_list:
        x += int(font.getlength(word))
    x += len(text_list) - 1

    return x
