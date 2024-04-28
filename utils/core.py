from PIL import Image, ImageDraw
from pilmoji import Pilmoji
from pilmoji.source import AppleEmojiSource
from typing import List, Tuple, Optional, Dict
from os import PathLike
from .helpers import background_standard_options


class Capture:
    """
    Main image rendering interface

    :param base: The background image of the text, needs to be 1080*1920 px
    :type base: PathLike
    :param avatar: The picture of the interlocutor, needs to be square
    :type avatar: PathLike
    :param conversation: The actual conversation to display
    :type conversation: List[Tuple[int, str]]
    :param name: The name of the interlocutor to display. Defaults to 'Antoine🥰'
    :type name: str, optional
    :param time: The time to display on the illustrations. Defaults to 21:48
    :type time: str, optional
    """

    def __init__(
            self,
            base: PathLike,
            avatar: PathLike,
            conversation: List[Tuple[int, str]],
            name: Optional[str] = 'Antoine🥰',
            time: Optional[str] = '21:48',
            emoji_in_name: Optional[bool] = True,
            preset_options: Optional[Dict] = background_standard_options,
            draw: Optional[ImageDraw.ImageDraw] = None
    ) -> None:
        self._base_path: PathLike = base
        self._avatar_path: PathLike = avatar
        self.conversation: List[Tuple[int, str]] = conversation
        self.name: str = name
        self.time: str = time
        self.emoji_in_name: bool = emoji_in_name
        self.preset_options: Dict = preset_options
        self.draw: ImageDraw.ImageDraw = draw
        self._new_draw: bool = False

        self.canvas: Image.Image = Image.new('RGBA', (1080, 1920))

    def add_background(self) -> None:
        """
        Adds the background to the canvas
        :return: None
        """

        with Image.open(self._base_path) as im:
            self.canvas.paste(im, (0, 0))

    def add_avatar(self) -> None:
        """
        Adds the avatar to the canvas
        :return: None
        """

        with Image.open(self._avatar_path) as im:
            avatar_size: Tuple[int, int] = background_standard_options['avatar_size']
            profile_resized = im.resize(avatar_size)
            self.canvas.paste(profile_resized, background_standard_options['avatar_position'], profile_resized)

    def add_name(self) -> None:
        """
        Adds the name of the interlocutor
        :return: None
        """

        with Pilmoji(self.canvas, source=AppleEmojiSource, emoji_position_offset=(2, 8),
                     emoji_scale_factor=1) as pilmoji:
            font = background_standard_options['name_font']
            text_length, w = pilmoji.getsize(self.name, font=font)
            x_pos = 540 - (text_length // 2)

            pilmoji.text((x_pos, background_standard_options['name_y_position']), self.name, (0, 0, 0), font)

    def add_time(self) -> None:
        """
        Adds the time on the canvas
        :return: None
        """

        self._create_draw()
        self.draw.text(background_standard_options['time_position'], self.time, (0, 0, 0),
                       font=background_standard_options['time_font'], anchor='ms')
        self._close_draw()

    def _create_draw(self) -> None:
        """
        Create a draw context
        :return: None
        """

        if self.draw is None:
            self.draw = ImageDraw.Draw(self.canvas)
            self._new_draw = True

    def _close_draw(self) -> None:
        """
        Close the Draw context
        :return: None
        """

        if self._new_draw:
            del self.draw
            self._new_draw = False
