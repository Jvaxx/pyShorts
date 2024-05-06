from utils import Capture, ScreenGenerator
from TextGen import TextGeneration, conversation_validation, VideoGenerator, TextToSpeechEleven
from pathlib import Path


conversation = [
    (False, 'Coucou!'),
    (True, 'Comment vas-tu?'),
    (False, 'Très bien, et toi, ça roule? 🤨')
    # (True, 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the \
    #        industry s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled'),
]


# generator = TextGeneration()
# res = []
# validated = False
# while not validated:
#     generator.generate_text()
#     res = generator.format_text()
#     validated = conversation_validation(res)
# del generator
# print(res)

vidGen = VideoGenerator('lenom', conversation)
vidGen.generate_video(pause_duration=0.3)


# tts = TextToSpeechEleven('Coucou, tu veux savoir un truc super drôle?')
# tts.generate_audio('./Generated/testie.mp3')

