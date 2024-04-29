from PIL import Image, ImageDraw
from pilmoji import Pilmoji, getsize
from pilmoji.source import AppleEmojiSource
from typing import List, Tuple, Optional, Dict
from os import PathLike
from .helpers import background_standard_options, format_text_box


class Capture:
    """
    Main image rendering interface

    :param base: The background image of the text, needs to be 1080*1920 px
    :type base: PathLike
    :param avatar: The picture of the interlocutor, needs to be square
    :type avatar: PathLike
    :param conversation: The actual conversation to display, the bool represents receiving, (ex, in iPhone preset, true
    means gray bubble and false means blue bubble)
    :type conversation: List[Tuple[bool, str]]
    :param name: The name of the interlocutor to display. Defaults to 'Antoine🥰'
    :type name: str, optional
    :param time: The time to display on the illustrations. Defaults to 21:48
    :type time: str, optional
    """

    def __init__(
            self,
            base: PathLike,
            avatar: PathLike,
            conversation: List[Tuple[bool, str]],
            name: Optional[str] = 'Antoine🥰',
            time: Optional[str] = '21:48',
            emoji_in_name: Optional[bool] = True,
            preset_options: Optional[Dict] = background_standard_options,
            draw: Optional[ImageDraw.ImageDraw] = None
    ) -> None:
        self._base_path: PathLike = base
        self._avatar_path: PathLike = avatar
        self.conversation: List[Tuple[bool, str]] = conversation
        self.name: str = name
        self.time: str = time
        self.emoji_in_name: bool = emoji_in_name
        self.preset_options: Dict = preset_options
        self.draw: ImageDraw.ImageDraw = draw
        self._new_draw: bool = False
        self.messages: List[MessageBox] = []
        self._import_messages()

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

    def add_messages(self) -> None:
        """
        Print the already rendered messages on the canvas
        :return: None
        """

        y = self.preset_options['message_first_y']
        for message in self.messages:
            x = message.get_message_box_x(self.preset_options['message_x_margin'])
            self.canvas.paste(message.canvas, (x, y), message.canvas)
            y += message.box_size[1] + self.preset_options['message_y_margin']

    def _import_messages(self) -> None:
        """
        Imports the conversation to the list of messages, and render them
        :return: None
        """

        for message in self.conversation:
            self.messages.append(MessageBox(message[1], message[0]))

        for message in self.messages:
            message.draw_background()
            message.draw_text()

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


class MessageBox:
    """
    Rendering interface of a message box. Usually used by class `Capture`but can be used to generate a standalone
    image of the message box.

    """

    def __init__(
            self,
            message_text: str,
            receiving: bool,
            preset_options: Optional[Dict] = background_standard_options,
            draw: Optional[ImageDraw.ImageDraw] = None
    ):
        self.preset_options: Dict = preset_options
        self.message_text: str = format_text_box(message_text, self.preset_options['message_max_width'],
                                                 self.preset_options['message_font'])
        self.text_size: Tuple[int, int] = getsize(self.message_text, font=self.preset_options['message_font'])
        self.box_size: Tuple[int, int] = (self.text_size[0] + 2*self.preset_options['message_x_padding'],
                                          self.text_size[1] + 2*self.preset_options['message_y_padding'])
        self.receiving: bool = receiving
        self.canvas: Image.Image = Image.new('RGBA', self.box_size)
        self.draw: ImageDraw.ImageDraw = draw
        self._new_draw: bool = False

    def draw_background(self) -> None:
        """
        Draws the background of the message box
        :return: None
        """

        self._create_draw()
        if self.receiving:
            self.draw.rounded_rectangle(
                [0, 0, *self.box_size],
                radius=self.preset_options['message_radius'],
                fill=self.preset_options['message_background_color_receiving'])
        else:
            self.draw.rounded_rectangle(
                [0, 0, *self.box_size],
                radius=self.preset_options['message_radius'],
                fill=self.preset_options['message_background_color_sending'])
        self._close_draw()

    def draw_text(self) -> None:
        """
        Draws the text of the message in the box
        :return: None
        """
        if not self.receiving:
            with Pilmoji(self.canvas, source=AppleEmojiSource, emoji_position_offset=(2, 8),
                         emoji_scale_factor=1) as pilmoji:
                pilmoji.text((self.preset_options['message_x_padding'], self.preset_options['message_y_padding']-10),
                             self.message_text, fill=(255, 255, 255, 255), font=self.preset_options['message_font'])
        else:
            with Pilmoji(self.canvas, source=AppleEmojiSource, emoji_position_offset=(2, 8),
                         emoji_scale_factor=1) as pilmoji:
                pilmoji.text((self.preset_options['message_x_padding'], self.preset_options['message_y_padding']-10),
                             self.message_text, fill=(0, 0, 0, 255), font=self.preset_options['message_font'])

    def get_message_box_x(self, message_x_margin: int) -> int:
        """
        Calculate the x coordinate of the message box

        :param message_x_margin: gap between border of the screen and message box
        :return: x coordinate of the upper left of the box
        """

        if self.receiving:
            return message_x_margin
        else:
            return 1080 - (self.box_size[0] + message_x_margin)

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
