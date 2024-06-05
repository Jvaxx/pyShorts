import os
import random
from PIL import Image, ImageDraw
from pilmoji import Pilmoji, getsize
from pilmoji.source import AppleEmojiSource
from typing import List, Tuple, Optional, Dict, Union
from os import PathLike
from .helpers import background_standard_options, format_text_box, choose_random_name, get_crop_region


class Intro_Image:
    """
    Interface for rendering intro image
    """

    def __init__(
            self,
            intro_text: str,
            preset_options: Optional[Dict] = background_standard_options
    ) -> None:
        self.preset_options = preset_options
        self.intro_text = format_text_box(intro_text, 1000, font=self.preset_options['intro_font'])
        self.background_path: str = preset_options['intro_background_directory']
        self.canvas: Image.Image = Image.new('RGB', (1080, 1920))
        self.draw: ImageDraw.Draw = None

        self.add_background()
        self.draw_text()

    def add_background(self):
        random_image = random.choice(os.listdir(self.background_path))
        print(random_image)
        im = self.resize_image(random_image)
        self.canvas.paste(im)


    def draw_text(self):

        self._create_draw()
        text_size = getsize(self.intro_text, font=self.preset_options['intro_font'])
        self.draw.rounded_rectangle(
            [540 - text_size[0]/2 - self.preset_options['intro_text_background_padding'],
             960 - text_size[1]/2 - self.preset_options['intro_text_background_padding'],
             540 + text_size[0]/2 + self.preset_options['intro_text_background_padding'],
             960 + text_size[1]/2 + self.preset_options['intro_text_background_padding']],
            radius=self.preset_options['intro_text_background_radius'],
            fill=(255, 255, 255, 0)
        )
        self._close_draw()

        with Pilmoji(self.canvas, source=AppleEmojiSource, emoji_position_offset=(2, 8),
                     emoji_scale_factor=1) as pilmoji:
            pilmoji.text((540, 930), self.intro_text, fill=(0, 0, 0, 255), font=self.preset_options['intro_font'], anchor='md', align='center', stroke_fill=(255,255,255,255), stroke_width=10)

    def save(self, path: str):
        self.canvas.save(path)

    def resize_image(self, image_name):
        with Image.open(self.background_path + image_name) as im:
            original_size = im.size
            if original_size[0]/original_size[1] < 9/16:  # image trop fine
                scale = 1080/original_size[0]
            else:  # trop large
                scale = 1920/original_size[1]

            # resize
            resized = im.resize((int(scale*original_size[0]), int(scale*original_size[1])))

        new_size = resized.size
        cropped = resized.crop(get_crop_region(new_size))
        return cropped

    def _create_draw(self) -> None:
        """
        Create a draw context
        :return: None
        """

        if self.draw is None:
            self.draw = ImageDraw.Draw(self.canvas, 'RGBA')
            self._new_draw = True

    def _close_draw(self) -> None:
        """
        Close the Draw context
        :return: None
        """

        if self._new_draw:
            del self.draw
            self._new_draw = False

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
    :param emoji_in_name: Is there an emoji in the name?
    :type emoji_in_name: bool, optional
    :param preset_options: The options of the preset, optional
    :param draw: the drawing context, optional
    """

    def __init__(
            self,
            base: PathLike,
            avatar: PathLike,
            conversation: List[Tuple[bool, str]],
            name: Optional[str] = 'Antoine🥰',
            time: Optional[str] = '21:48',
            preset_options: Optional[Dict] = background_standard_options,
            draw: Optional[ImageDraw.ImageDraw] = None,
            message_area: Optional = None,
    ) -> None:
        self._base_path: PathLike = base
        self._avatar_path: PathLike = avatar
        self.conversation: List[Tuple[bool, str]] = conversation
        self.name: str = name
        self.time: str = time
        self.preset_options: Dict = preset_options
        self.draw: ImageDraw.ImageDraw = draw

        self._new_draw: bool = False
        self._generated: bool = False
        self.messages: List[MessageBox] = []

        self._import_messages()
        self.message_area: MessageArea = message_area
        self.canvas: Image.Image = Image.new('RGBA', (1080, 1920))

    def generate(self, scroll: Optional[float] = 1.0) -> None:
        """
        Generates the picture
        :param scroll: scroll value (0-1) (defaults to 1)
        :return: None
        """

        if not self._generated:
            self._add_background()
            self._add_name()
            self._add_avatar()
            self._add_time()
            self._add_messages(scroll)
            self._generated = True
        else:
            print('capture already generated')

    def _add_background(self) -> None:
        """
        Adds the background to the canvas
        :return: None
        """

        with Image.open(self._base_path) as im:
            self.canvas.paste(im, (0, 0))

    def _add_avatar(self) -> None:
        """
        Adds the avatar to the canvas
        :return: None
        """

        with Image.open(self._avatar_path) as im:
            avatar_size: Tuple[int, int] = background_standard_options['avatar_size']
            profile_resized = im.resize(avatar_size)
            self.canvas.paste(profile_resized, background_standard_options['avatar_position'], profile_resized)

    def _add_name(self) -> None:
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

    def _add_time(self) -> None:
        """
        Adds the time on the canvas
        :return: None
        """

        self._create_draw()
        self.draw.text(background_standard_options['time_position'], self.time, (0, 0, 0),
                       font=background_standard_options['time_font'], anchor='ms')
        self._close_draw()

    def _add_messages(self, scroll: Optional[float] = 1.0) -> None:
        """
        Print the already rendered messages on the canvas
        :return: None
        """

        y = self.preset_options['message_first_y']

        if self.message_area is None:
            self.message_area = MessageArea(self.messages, scroll, self.preset_options)

        self.canvas.paste(self.message_area.canvas, (0, y), self.message_area.canvas)

    def save(self, path: Union[PathLike, str], scroll: Optional[float] = 1.0) -> None:
        """
        Saves the capture into the specified path. Generate the capture if needed.
        :param scroll: scroll value (0-1). Optional, defaults to 1 and used if not generated.
        :param path: the path. PathLike object
        :return: None
        """

        if not self._generated:
            self.generate(scroll)

        self.canvas.save(path)

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
        self.box_size: Tuple[int, int] = (self.text_size[0] + 2 * self.preset_options['message_x_padding'],
                                          self.text_size[1] + 2 * self.preset_options['message_y_padding'])
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
                pilmoji.text((self.preset_options['message_x_padding'], self.preset_options['message_y_padding'] - 10),
                             self.message_text, fill=(255, 255, 255, 255), font=self.preset_options['message_font'])
        else:
            with Pilmoji(self.canvas, source=AppleEmojiSource, emoji_position_offset=(2, 8),
                         emoji_scale_factor=1) as pilmoji:
                pilmoji.text((self.preset_options['message_x_padding'], self.preset_options['message_y_padding'] - 10),
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


class MessageArea:
    """
    Rendering the messages in this area. Using MessageBox class and used in Capture class
    """

    def __init__(
            self,
            message_list: List[MessageBox],
            scroll: Optional[float] = 1.0,
            preset_options: Optional[Dict] = background_standard_options,
            draw: Optional[ImageDraw.ImageDraw] = None,
    ):
        self.message_list: List[MessageBox] = message_list
        self.scroll: float = scroll
        self.preset_options: Dict = preset_options
        self.draw: ImageDraw.ImageDraw = draw

        self._new_draw: bool = False
        self._total_message_height: int = self.get_total_message_height()
        self.canvas: Image.Image = Image.new('RGBA', self.preset_options['message_area_size'])
        self.add_messages()

    def add_messages(self) -> None:
        """
        Draws the messages on the canvas
        :return: None
        """

        y = -int(self.scroll * max(0, self._total_message_height - self.preset_options['message_area_size'][1])) + \
            self.preset_options['message_y_margin']
        print(f'\rMessageArea INFO: generation de l\'image: {len(self.message_list)}', end="")
        for message in self.message_list:
            x = message.get_message_box_x(self.preset_options['message_x_margin'])
            self.canvas.paste(message.canvas, (x, y), message.canvas)
            y += message.box_size[1] + self.preset_options['message_y_margin']

    def get_total_message_height(self) -> int:
        """
        Calculate the total height of messages, margins included.
        :return: total height, int
        """

        h = self.preset_options['message_y_margin']
        for message in self.message_list:
            h += message.box_size[1] + self.preset_options['message_y_margin']
        return int(h)


class ScreenGenerator:
    """
    Main interface to generate multiple screenshots of one conversation. Uses the Capture class
    """

    def __init__(
            self,
            conversation: List[Tuple[bool, str]],
            preset: Optional[Dict] = background_standard_options,
            name: Optional[str] = 'Antoine🥰',
            time: Optional[str] = '21:48',
    ):
        self.conversation: List[Tuple[bool, str]] = conversation
        self.preset: Dict = preset
        self.name: str = name
        self.time: str = time
        self.capture_list: List[Capture] = []

        if self.name == 'Antoine🥰' and self.preset['name_list_path']:
            self.name = choose_random_name(self.preset['name_list_path'])

        self._add_captures()

    def _add_captures(self) -> None:
        """
        Adds captures to the capture list. Captures are not yet generated.
        :return: None
        """
        for i in range(len(self.conversation)):
            self.capture_list.append(Capture(
                self.preset['background_path'],
                self.preset['avatar_path'],
                self.conversation[:i+1],
                name=self.name,
                time=self.time,
                preset_options=self.preset
            ))

    def save_captures(self, path: str) -> None:
        """
        Saves all the capture in a given path
        :return: None
        """

        for i, capture in enumerate(self.capture_list):
            capture.save(path + '{:02d}'.format(i) + '.png')
