from utils import Capture, ScreenGenerator
from TextGen import TextGeneration, conversation_validation, TextToSpeech, VideoGenerator
from pathlib import Path


conversation = [
    (False, 'Coucou!'),
    (True, 'Comment vas-tu?'),
    (False, 'Très bien, et toi, ça roule? 🤨'),
    (True, 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the \
           industry s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled'),
    (False, 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the \
            industry s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled'),
    # (True, 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the \
    #        industry s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled'),
]


generator = TextGeneration()
res = []
validated = False
while not validated:
    generator.generate_text()
    res = generator.format_text()
    validated = conversation_validation(res)
del generator
print(res)

vidGen = VideoGenerator('lenom', res)
vidGen.generate_video(pause_duration=0.3)

# conv = ScreenGenerator(res)
# conv.save_captures('./Generated/capt')

