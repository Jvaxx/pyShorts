from TextGen import VideoGenerator, BatchTextGenerator, BatchVideoGeneratorFromFile, read_stats
from utils import Intro_Image, choose_random_name
import json

conversation = [
    (False, 'Eh, tu connais l\'histoire du petit dej ?'),
    # (True, 'Euh non 🤨'),
    # (False, 'Pas de bol... 🥣'),
    # (True, 'Pff... C\'est pas drôle.'),
    # (False, 'Et tu connais l\'histoire du pingouin qui respire par les fesses ? 🐧'),
    # (True, 'Laisse moi deviner, il s\'assoit et il meurt ?'),
    # (False, 'Ah voila, tu commences à comprendre!'),
    # (False, 'Eh, tu connais l\'histoire du petit dej ?'),
    # (True, 'Euh non 🤨'),
    # (False, 'Pas de bol... 🥣'),
    # (True, 'Pff... C\'est pas drôle.'),
    # (False, 'Et tu connais l\'histoire du pingouin qui respire par les fesses ? 🐧'),
    # (True, 'Laisse moi deviner, il s\'assoit et il meurt ?'),
    # (False, 'Ah voila, tu commences à comprendre!'),
]


# generator = BatchTextGenerator()
# stop = False
# while not stop:
#     theme = input("thème: ")
#     generator.trial_generation(theme)
#     inp = input("Arrêter ici? (o/n): ")
#     if inp in ["o", "O", "y","Y"]:
#         stop = True

# for i, convo in enumerate(generator.conversations):
#     vidGen = VideoGenerator('vid' + str(i), convo)
#     vidGen.generate_video(pause_duration=0)

b = BatchVideoGeneratorFromFile()
# b.add_conversation()
b.generate_videos(background_music_level=-15)



# vidGen = VideoGenerator('vid0', conversation, intro_message="POV: Je l'invite chez moi le soir")
# vidGen.generate_video(pause_duration=0.7, use_generated_captures=False, use_generated_audios=True)
