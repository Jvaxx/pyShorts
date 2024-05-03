from llama_cpp import Llama
from typing import List, Optional, Union, Tuple
from urllib.parse import urlencode
import httplib2
import movis as mv
from utils import ScreenGenerator


class TextGeneration:

    def __init__(self):
        self.prompt: str = 'Deux amis parlent par SMS. Les messages sont courts. Le ton est détendu. Ils ont de l\'humour. Il y a une tension sexuelle entre eux et des sous-entendus sexuels. Pas d\'explication a la fin de la conversation. Pas de traduction. L\'échange s\'arrête au bout de 10 répliques.\n'
        self.first_messages: str = 'A: J\'ai une blague pour toi.\nB: Ah oui, dis moi.\nA: '
        self.model = Llama('Ressources/mistral-7b-instruct-v0.2.Q4_0.gguf', n_gpu_layers=-1, chat_format='llama-2')
        self.result = None

    def generate_text(self):
        self.result = self.model(self.prompt + self.first_messages, max_tokens=None, echo=True)

    def get_raw_text(self):
        return self.result['choices'][0]['text']

    def format_text(self) -> List:
        split = self.result['choices'][0]['text'].split('\n')[1:12]
        res = []

        for line in split:
            if line[:2] == 'A:':
                res.append((False, line[3:]))
            elif line[:2] == 'B:':
                res.append((True, line[3:]))
            else:
                print('ERROR: format text impossible')
                print(line[:2])
        return res


class TextToSpeech:
    """
    TTS Generator
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
            generator = TextToSpeech(replica[1])
            generator.generate_audio(path + 'aud{:02d}'.format(i) + '.wav')
            print('generated audio ' + str(i))
        self._audio_files_generated = True

    def generate_audio_layers(self, path: str) -> None:
        """
        Generate the audio layers of each file
        :param path: the path to the audio file. Do not include the digits at the end nor the extension
        :return: None
        """

        if not self._audio_files_generated:
            self.generate_audio_files(path)

        for i in range(len(self.conversation)):
            file_path = path + f"aud{'{:02d}'.format(i)}.wav"
            self._audio_layers.append(mv.layer.media.Audio(file_path))

    def get_duration(self, pause_duration: Optional[float] = 1.0) -> float:
        duration = 0.0
        for audio in self._audio_layers:
            duration += audio.duration + pause_duration
        return duration

    def generate_image_layers(self, path: str) -> None:
        screen_gen = ScreenGenerator(self.conversation)
        screen_gen.save_captures(path + 'capt')

        for i in range(len(self.conversation)):
            file_path = path + f"capt{'{:02d}'.format(i)}.png"
            self._image_layers.append(mv.layer.media.Image(file_path))

    def generate_video(self, path: Optional[str] = './Generated/', pause_duration: Optional[float] = 1.0):
        """
        Generates the video
        :param path:
        :return:
        """
        print('generating image layers')
        self.generate_image_layers(path)
        print('generating audio layers')
        self.generate_audio_layers(path)

        scene = mv.layer.Composition(size=(1080, 1920), duration=self.get_duration(pause_duration))

        time: float = 0.0
        for i, image_layer in enumerate(self._image_layers):
            scene.add_layer(image_layer, offset=time, end_time=time+self._audio_layers[i].duration+pause_duration)
            scene.add_layer(self._audio_layers[i], offset=time)
            time += self._audio_layers[i].duration+pause_duration

        scene.write_video(path + 'resultat.mp4')