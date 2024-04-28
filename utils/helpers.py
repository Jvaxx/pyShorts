from typing import Dict, Any
from PIL import ImageFont

background_standard_options: Dict[str, Any] = {
    'name_y_position': 290,
    'avatar_size': (180, 180),
    'avatar_position': (450,100),
    'name_font': ImageFont.truetype(font='utils/fonts/OpenSans-Regular.ttf', size=35),
    'time_position': (115, 85),
    'time_font': ImageFont.truetype(font='utils/fonts/OpenSans-Bold.ttf', size=45),
}