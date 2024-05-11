import os
import random
from llama_cpp import Llama
from typing import List, Optional, Union, Tuple
from urllib.parse import urlencode
import httplib2
import movis as mv
from utils import ScreenGenerator
from .helpers import tts_settings, send_request, generate_rotation_frames, generate_scale_frames, send_request_stream, format_text, conversation_validation
import requests
import time


class TextGeneration:
    """
    Uses llama.cpp local
    """
    def __init__(self):
        self.prompt: str = 'Deux amis s\'échangent des messages courts. La converstion est très courte (6 messages au maximum). Le ton est chaleureux. La conversation est drôle. Il y a une blague. Pas de traduction de la conversatoin. Pas d\'explication de la conversation. \n'
        self.first_messages: str = 'A: Salut!\nB: Qu\'est-ce que tu veux encore 🤨\nA: '
        self.model = Llama('models/Meta-Llama-3-8B-Instruct-Q6_K.gguf', n_gpu_layers=-1, chat_format='llama-3')
        self.result = None

    def generate_text(self):
        self.result = self.model(self.prompt + self.first_messages, max_tokens=None, echo=True)

    def get_raw_text(self):
        return self.result['choices'][0]['text']

    def format_text(self) -> List:
        return format_text(self.result['choices'][0]['text'])


class TextGenerationOllama:
    """
    Uses Ollama's llama3 with a custon modelfile
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
            res = send_request(tts_settings['eleven_api_url'] + tts_settings['voice_id'], json=data,
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


class TextToSpeechMaryTTS:
    """
    TTS Generator using marytts. Absolute trash quality. Use of tts eleven recommended
    """

    def __init__(
            self,
            input_text: str,
            mary_host: Optional[str] = 'localhost',
            mary_port: Optional[Union[str, int]] = '59125'
    ):
        self.input_text: str = input_text
        self.mary_host: str = mary_host
        self.mary_port: str = str(mary_port)

    def generate_audio(self, path: str) -> None:
        """
        Generate the TTS and saves it
        :param path: path to audio
        :return: None
        """

        query_hash = {"INPUT_TEXT": self.input_text,
                      "INPUT_TYPE": "TEXT",  # Input text
                      "LOCALE": "fr",
                      "VOICE": "upmc-pierre-hsmm",  # Voice informations  (need to be compatible)
                      "OUTPUT_TYPE": "AUDIO",
                      "AUDIO": "WAVE",  # Audio informations (need both)
                      }
        query = urlencode(query_hash)

        h_mary = httplib2.Http()
        resp, content = h_mary.request("http://%s:%s/process?" % (self.mary_host, self.mary_port), "POST", query)

        if resp["content-type"] == "audio/x-wav":
            # Write the wav file
            f = open(path, "wb")
            f.write(content)
            f.close()
        else:
            Exception(content)


class VideoGenerator:
    """
    Main video rendering interface
    """

    def __init__(
            self,
            video_name: str,
            conversation: List[Tuple[bool, str]]
    ):
        self.video_name: str = video_name
        self.conversation: List[Tuple[bool, str]] = conversation

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

        for i in range(len(self.conversation)):
            file_path = path + f"{self.video_name}_capt_{'{:02d}'.format(i)}.png"
            self._image_layers.append(mv.layer.media.Image(file_path))

    def generate_video(
            self,
            path: Optional[str] = './Generated/',
            pause_duration: Optional[float] = 1.0,
            background_music: Optional[Union[None, str]] = tts_settings['default_background_music'] + str(int(random.randint(1, 2))),
            use_generated_audios: Optional[bool] = False,
            use_generated_captures: Optional[bool] = False,
            use_background_video: Optional[bool] = True,
    ):
        """
        Generates the video
        :param path: the path to the result folder
        :param pause_duration: delay btw each audio files
        :param background_music: background music name (folder: Ressources/sounds)
        :param use_generated_audios: if true, there will not be any TTS generation.
        :param use_generated_captures: if true, there will not be any capture generation.
        :param use_background_video: use an animated background
        :return: None
        """
        os.mkdir(os.path.join(path, self.video_name))
        print('VideoGenerator INFO: generating image layers')
        self.generate_image_layers(path + self.video_name + '/', use_generated_captures=use_generated_captures)
        print('\nVideoGenerator INFO: generating audio layers')
        self._audio_files_generated = use_generated_audios
        self.generate_audio_layers(path + self.video_name + '/')
        total_duration = self.get_duration(pause_duration)
        scene = mv.layer.Composition(size=(1080, 1920), duration=total_duration)
        super_scene = mv.layer.Composition(size=(1080, 1920), duration=total_duration)

        if use_background_video:
            bg_video = mv.layer.media.Video('./Ressources/satisfying background.mp4', audio=False)
            super_scene.add_layer(bg_video, scale=2.666, offset=-int(random.randrange(10, 120)))

        time_stamp: float = 0.0
        for i, image_layer in enumerate(self._image_layers):
            if i == len(self._image_layers) - 1:  # The last image, adding delay at the end
                scene.add_layer(image_layer, offset=time_stamp, end_time=time_stamp + self._audio_layers[i].duration + pause_duration + tts_settings['end_delay'])
            else:
                scene.add_layer(image_layer, offset=time_stamp, end_time=time_stamp + self._audio_layers[i].duration + pause_duration)

            scene.add_layer(self._audio_layers[i], offset=time_stamp)
            time_stamp += self._audio_layers[i].duration + pause_duration

        if background_music:
            bg_music_layer = mv.layer.media.Audio('Ressources/sounds/' + background_music + '.mp3')
            scene.add_layer(bg_music_layer, end_time=total_duration, audio_level=-10, offset=-0.5)

        if not use_background_video:
            super_scene.add_layer(scene, name='msg')
        else:
            super_scene.add_layer(scene,scale=0.7, name='msg', opacity=0.9)
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
