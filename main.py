from utils import Capture
from pathlib import Path

test = Capture(Path('./Ressources/base sms iphone.png'), Path('./Ressources/profile default.png'),
               [(0, 'Bonjour'), (1, 'Salut')])

test.add_background()
test.add_avatar()
test.add_name()
test.add_time()
test.canvas.show()
