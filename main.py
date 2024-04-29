from utils import Capture
from pathlib import Path


conversation = [
    (False, 'Coucou!'),
    (True, 'Comment vas-tu?'),
    (False, 'Très bien, et toi, ça roule? 🤨'),
]
test = Capture(Path('./Ressources/base sms iphone.png'), Path('./Ressources/profile default.png'),
               conversation, name='Coucou🚀')


test.add_background()
test.add_avatar()
test.add_name()
test.add_time()
test.add_messages()

test.canvas.show()

# msg_box = MessageBox('Bonjour!', True)
# msg_box.draw_background()
# msg_box.draw_text()
# msg_box.canvas.show()
