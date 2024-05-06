from typing import List


tts_settings = {
    'eleven_api_key': '814767ed0e23c7bec4a65b85562fa6e2',
    'voice_id': 'HDc7042zGcc1SdpT2m1U',
    'eleven_api_url': 'https://api.elevenlabs.io/v1/text-to-speech/'
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



