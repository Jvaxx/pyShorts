from utils import Capture
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
test = Capture(Path('./Ressources/base sms iphone.png'), Path('./Ressources/profile default.png'),
               conversation, name='Coucou🚀')


test.add_background()
test.add_avatar()
test.add_name()
test.add_time()
test.add_messages(scroll=0)
test.canvas.show()

# msg_box = MessageBox('Bonjour!', True)
# msg_box.draw_background()
# msg_box.draw_text()
# msg_box.canvas.show()
