import os
import random
import movis as mv
from utils import ScreenGenerator, Intro_Image
from .helpers import *
import requests
import time
import uuid


class TextGenerationOllama:
    """
    Uses Ollama's llama3 with a custom model file
    """
    def __init__(self, theme: str):
        self.prompt: str = "Génère une conversation humouristique sur le thème de " + theme + " en français. Le ton est décontracté. Les deux interlocuteurs seront exactement nommés A: et B:"
        self.result = None
        self.result_formatted = None

    def generate_text(self) -> List:
        body = {
            "model": "conv1",
            "prompt": self.prompt
        }
        self.result = send_request_stream("http://localhost:11434/api/generate", body)
        self.result_formatted = format_text(self.result)
        return self.result_formatted


class BatchTextGenerator:
    """
    Handle a batch text generation
    """
    def __init__(self):
        self.conversations: List[List[Tuple[bool, str]]] = []

    def trial_generation(self, theme: str) -> None:
        """
        Generate a conversation to be verified
        :param theme: theme that will be fed to the prompt
        :return: None
        """
        conv = TextGenerationOllama(theme).generate_text()
        if conversation_validation(conv):
            self.conversations.append(conv)


class TextToSpeechEleven:
    """
    TTS Generator using ElevenLabs
    """

    def __init__(
            self,
            input_text: str
    ):
        self.input_text: str = input_text
        self._request_made: bool = False
        self._response: Union[requests.Response, None] = None

    def make_request(self):
        """
        generates a request
        :return: request response
        """

        if self._request_made:
            print('TTSEleven ERROR: make_request called while it has already been called on this object.')
        else:
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": tts_settings['eleven_api_key']
            }
            data = {
                "text": self.input_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.7,
                    "style": 0.5
                }
            }
            res = send_request(tts_settings['eleven_api_url'] + tts_settings['voice_id'], json_data=data,
                               headers=headers)
            if res.status_code != 200:
                print('TTSEleven ERROR: request failed, error: ', res.status_code)
                raise Exception()
            time.sleep(1)
            return res

    def generate_audio(self, path: str) -> None:
        """
        Generates audio file
        :param path: path to the audio file including the extension .mp3
        :return: None
        """

        response = self.make_request()
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        print('TTSEleven INFO: audio written')


class VideoGenerator:
    """
    Main video rendering interface
    If intro_message parameter is left empty, there will be no intro image.
    """

    def __init__(
            self,
            video_name: str,
            conversation: List[Tuple[bool, str]],
            intro_message: Optional[Union[None, str]] = None,
            conversation_uuid: Optional[Union[uuid.UUID, int]] = 0
    ):
        self.video_name: str = video_name
        self.conversation: List[Tuple[bool, str]] = conversation
        self.intro_message: Optional[Union[None, str]] = intro_message
        self.conversation_uuid: Optional[Union[uuid.UUID, int]] = conversation_uuid

        self._audio_files_generated: bool = False
        self._audio_layers: List[mv.layer.media.Audio] = []  # each audio corresponds to a message of the conversation

        self._image_layers: List[mv.layer.media.Image] = []  # each image corresponds to a message of the conversation

    def generate_audio_files(self, path: str) -> None:
        """
        Generate the audio files of each replica
        :return: None
        """

        for i, replica in enumerate(self.conversation):
            generator = TextToSpeechEleven(replica[1])
            generator.generate_audio(path + f"{self.video_name}_aud_{'{:02d}'.format(i)}.mp3")
            print('VideoGenerator INFO: generated audio file ' + str(i))

        if self.intro_message:
            generator = TextToSpeechEleven(self.intro_message)
            generator.generate_audio(path + f"{self.video_name}_aud_intro.mp3")

        save_characters("./data/stat.txt", self.conversation, self.conversation_uuid, self.intro_message)
        self._audio_files_generated = True

    def generate_audio_layers(self, path: str) -> None:
        """
        Generate the audio layers of each file
        :param path: the path to the audio file. Do not include the digits at the end nor the extension
        :return: None
        """

        if not self._audio_files_generated:
            self.generate_audio_files(path)
        time.sleep(2)

        if self.intro_message:
            file_path = path + f"{self.video_name}_aud_intro.mp3"
            self._audio_layers.append(mv.layer.media.Audio(file_path))
        for i in range(len(self.conversation)):
            file_path = path + f"{self.video_name}_aud_{'{:02d}'.format(i)}.mp3"
            self._audio_layers.append(mv.layer.media.Audio(file_path))

    def get_duration(self, pause_duration: Optional[float] = 1.0) -> float:
        duration = tts_settings['end_delay']  # adding 3s for the end
        for audio in self._audio_layers:
            duration += audio.duration + pause_duration
        return duration

    def generate_image_layers(self, path: str, use_generated_captures: Optional[bool] = False) -> None:
        if not use_generated_captures:
            screen_gen = ScreenGenerator(self.conversation)
            screen_gen.save_captures(path + f'{self.video_name}_capt_')
        if self.intro_message:
            intro_gen = Intro_Image(self.intro_message)
            intro_gen.save(path + f"{self.video_name}_capt_intro.png")
            self._image_layers.append(mv.layer.media.Image(path + f"{self.video_name}_capt_intro.png"))
        for i in range(len(self.conversation)):
            file_path = path + f"{self.video_name}_capt_{'{:02d}'.format(i)}.png"
            self._image_layers.append(mv.layer.media.Image(file_path))

    def generate_video(
            self,
            path: Optional[str] = './Generated/',
            pause_duration: Optional[float] = 0,
            background_music_file: Optional[Union[None, str]] = tts_settings['background_music_folder'],
            background_music_level: Optional[int] = -10,
            use_generated_audios: Optional[bool] = False,
            use_generated_captures: Optional[bool] = False,
            use_background_video: Optional[bool] = True
    ):
        """
        Generates the video
        :param background_music_level: level of background music in decibels. Defaults to -10.
        :param path: the path to the result folder
        :param pause_duration: delay btw each audio files
        :param background_music_file: background music name folder. To not use music, set the param to None.
        :param use_generated_audios: if true, there will not be any TTS generation.
        :param use_generated_captures: if true, there will not be any capture generation.
        :param use_background_video: use an animated background
        :return: None
        """
        if (not use_generated_captures) and (not use_generated_audios):
            os.mkdir(os.path.join(path, self.video_name))
        print('VideoGenerator INFO: generating image layers')
        self.generate_image_layers(path + self.video_name + '/', use_generated_captures=use_generated_captures)
        print('\nVideoGenerator INFO: generating audio layers')
        self._audio_files_generated = use_generated_audios
        self.generate_audio_layers(path + self.video_name + '/')
        total_duration = self.get_duration(pause_duration)
        scene_message = mv.layer.Composition(size=(1080, 1920), duration=total_duration)
        scene_background = mv.layer.Composition(size=(1080, 1920), duration=total_duration)
        super_scene = mv.layer.Composition(size=(1080, 1920), duration=total_duration)
        intro_scene = mv.layer.Composition(size=(1080, 1920), duration=total_duration)

        if use_background_video:
            bg_video = mv.layer.media.Video('./Ressources/satisfying background.mp4', audio=False)
            scene_background.add_layer(bg_video, scale=2.666, offset=-int(random.randrange(20, 250)))
            super_scene.add_layer(scene_background, offset=0)

        time_stamp: float = 0.0
        for i, image_layer in enumerate(self._image_layers):
            if i == 0 and self.intro_message:  # The intro image
                intro_scene.add_layer(image_layer, offset=time_stamp, end_time=time_stamp + self._audio_layers[i].duration + pause_duration)
                intro_scene.add_layer(self._audio_layers[i], offset=time_stamp)
            elif i == len(self._image_layers) - 1:  # The last image, adding delay at the end
                scene_message.add_layer(image_layer, offset=time_stamp, end_time=time_stamp + self._audio_layers[i].duration + pause_duration + tts_settings['end_delay'])
                scene_message.add_layer(self._audio_layers[i], offset=time_stamp)
            else:
                scene_message.add_layer(image_layer, offset=time_stamp, end_time=time_stamp + self._audio_layers[i].duration + pause_duration)
                scene_message.add_layer(self._audio_layers[i], offset=time_stamp)

            time_stamp += self._audio_layers[i].duration + pause_duration

        if background_music_file:
            bg_music_layer = mv.layer.media.Audio(background_music_file + random.choice(os.listdir(background_music_file)))
            scene_message.add_layer(bg_music_layer, end_time=total_duration, audio_level=background_music_level, offset=-0.5)

        if not use_background_video:
            super_scene.add_layer(intro_scene, name='intro')
            super_scene.add_layer(scene_message, name='msg')
        else:
            super_scene.add_layer(intro_scene, name='intro')
            super_scene.add_layer(scene_message,scale=0.7, name='msg', opacity=0.9)
            keyframes, values = generate_rotation_frames(total_duration, cycle_time=1.5)
            super_scene['msg'].rotation.enable_motion().extend(
                keyframes=keyframes.tolist(),
                values=values.tolist(),
                easings=None
            )
            keyframes, values = generate_scale_frames(total_duration, cycle_time=3, base_scale=0.8)
            super_scene['msg'].scale.enable_motion().extend(
                keyframes=keyframes.tolist(),
                values=values.tolist(),
                easings=None
            )

        super_scene.write_video(path + self.video_name + '.mp4')


class BatchVideoGeneratorFromFile:
    """
    Video rendering interface using conversations from a file.
    File format: List[Dict['intro': Union[none, str], 'conversation': List[bool, str], 'uuid': UUID]] in JSON format
    """
    def __init__(
            self,
            conv_file: Optional[str] = './Ressources/conversations.txt'
    ):
        self.conv_file: str = conv_file

    def add_conversation(self):
        print("Enter/Paste your content.")
        contents = []
        stop = 0
        while True:
            line = input()
            if line:
                stop = 0
                contents.append(line)
            elif stop < 1:
                stop += 1
            else:
                print('OK.')
                break

        contents = format_text(list(filter(lambda a: a != '', contents)))
        id = uuid.uuid4()
        print('')
        title = input("Titre (laisser vide sinon): ")
        if title == "":
            title = None

        dico = {"intro": title, "conversation": contents, "uuid": str(id)}
        conv_list = []
        if os.path.isfile(self.conv_file):
            with open(self.conv_file, 'r', encoding="utf-8") as f:
                conv_list = json.load(f)
        conv_list.append(dico)

        with open(self.conv_file, 'w', encoding="utf-8") as f:
            json.dump(conv_list, f, ensure_ascii=False)

    def generate_videos(self, max: int = 10, **kwargs):
        stats = read_stats('./data/stat.txt')
        conversations_data = read_stats(self.conv_file)[0]

        count = 0
        conv_num = 0
        while count < max:
            if conv_num >= len(conversations_data):
                print('not enough conversations stored')
                break
            conv_data = conversations_data[conv_num]
            if not is_used(stats, conv_data["uuid"]):
                vidGen = VideoGenerator("vid"+str(count), conv_data["conversation"], intro_message=conv_data["intro"], conversation_uuid=conv_data["uuid"])
                vidGen.generate_video(**kwargs)
                count += 1
            conv_num += 1
