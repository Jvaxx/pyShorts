import json
import time
from datetime import date
from typing import List, Tuple, Optional, Union, Dict
import requests
import numpy as np



tts_settings = {
    'eleven_api_key': '814767ed0e23c7bec4a65b85562fa6e2',
    'voice_id': 'EmZGlxI7QPvCEMOkFhB9',
    'eleven_api_url': 'https://api.elevenlabs.io/v1/text-to-speech/',
    'default_background_music': 'funny_music',
    'end_delay': 3.0,
}


def conversation_validation(conversation: List) -> bool:
    """
    Visualize the conversation before validation
    :param conversation: List of formatted conversation ex: [(True, 'blabla'), (False, 'blabla')]
    :return: bool
    """

    for replica in conversation:
        pr = ''
        if replica[0]:
            pr += 'Personne 2: '
        else:
            pr += 'Personne 1: '
        print(pr + replica[1])

    inp = False
    ans = input('Conv ok ? (o/n): ')

    if ans in ['o', 'O', 'y', 'Y']:
        inp = True

    return inp


def character_counter_string(text: str) -> int:
    """
    Counts the number of characters in a string
    :param text: the text to count
    :return: number of character
    """
    return len(text)


def conversation_character_counter(conv: List[Tuple[bool, str]]) -> int:
    """
    Returns the number of characters of a conversation
    :param conv: the conversation
    :return: number of character
    """

    total = 0
    for replica in conv:
        total += character_counter_string(replica[1])
    return total


def save_characters(path: str, conv: List[Tuple[bool, str]], conv_uuid: Union[str, int], intro_message: Optional[Union[None, str]] = None) -> None:
    """
    save the number of char of a conversation in a file
    :param conv_uuid: uuid of conversation. If it's not relevant, use 0 instead.
    :param intro_message: the string of the intro image. If left empty it will not be used. Defaults to None.
    :param path: where to save
    :param conv: conversation
    :return: none
    """

    intro_length = 0
    if intro_message: intro_length = character_counter_string(intro_message)
    to_save = {"date": date.today().isoformat(), "length": conversation_character_counter(conv) + intro_length, "uuid": conv_uuid}
    with open(path, "a") as f:
        f.write(json.dumps(to_save) + "\n")


def read_stats(path: str) -> List[Dict]:
    """
    Reads the stats (used to verify uuid of conversation in order to not use them twice)
    :param path: path to stats file
    :return: list of stats
    """
    res = []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            res.append(json.loads(line))
    return res


def is_used(stats: List[Dict], id: Union[str, int]) -> bool:
    for stat in stats:
        if stat["uuid"] == id:
            return True
    return False


def send_request(url, json_data, headers):
    response = None
    wait = True
    while wait:
        print('TextGenHelper send_request INFO: Sending request...')
        response = requests.post(url, json=json_data, headers=headers)
        if response.status_code == 429:
            print('TextGenHelper send_request ERROR: 429, retrying in 10s...')
            time.sleep(10)
        elif response.status_code != 200:
            print('TextGenHelper send_request ERROR:', response.status_code)
            raise Exception
        else:
            # print('TextGenHelper send_request INFO: Request successfull (200)')
            wait = False

    return response


def send_request_stream(url: str, json_data: dict):
    response_text = ''
    s = requests.Session()
    print("TextGenHelper send_request_stream INFO: sending request.")
    with s.post(url, json=json_data, headers=None, stream=True) as res:
        for line in res.iter_lines():
            if line:
                response_text += json.loads(line.decode("UTF-8"))["response"]
    # print("TextGenHelper send_request_stream INFO: request done.")
    return response_text


def format_text(text_to_format: Union[str, List]) -> List:
    if isinstance(text_to_format, str):
        split = text_to_format.split('\n')[1:]
    else:
        split = text_to_format
    res = []

    for line in split:
        if line[:2] == 'A:':
            res.append((False, line[3:]))
        elif line[:3] == 'A :':
            res.append((False, line[4:]))
        elif line[:2] == 'B:':
            res.append((True, line[3:]))
        elif line[:3] == 'B :':
            res.append((True, line[4:]))
        else:
            print('ERROR: format text impossible')
            print(line[:3])
    return res


def generate_rotation_frames(duration: float, cycle_time: Optional[float] = 1) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates the animation data (keyframes and value)
    :param duration: the duration of the video
    :param cycle_time: the length in seconds of a cycle. Defaults to 1
    :return: tuple of keyframes list and values list
    """

    keyframes = np.round(np.linspace(0, duration, num=int(duration/cycle_time)*4), decimals=1)
    values = np.array([(i % 2) * 1.5 * ((i % 4)-2) for i in range(len(keyframes))])

    return keyframes, values


def generate_scale_frames(duration: float, cycle_time: Optional[float] = 4, base_scale: Optional[float] = 0.7) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates the animation data (keyframes and value)
    :param duration: the duration of the video
    :param cycle_time: the length in seconds of a cycle. Defaults to 1
    :param base_scale: base scale. Defaults to 0.7
    :return: tuple of keyframes list and values list
    """

    keyframes = np.round(np.linspace(0, duration, num=int(duration/cycle_time)*4), decimals=1)
    list_of_values = [base_scale, base_scale*1.03, base_scale, base_scale*0.97]
    values = np.array([list_of_values[i % 4] for i in range(len(keyframes))])

    return keyframes, values

