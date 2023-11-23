import aiohttp
import asyncio
import json

from loguru import logger

from words import words as words_list


def get_url(word: str) -> str:
    return f"https://dictionary.skyeng.ru/api/public/v1/words/search?search={word}&page=1&pageSize=1"


async def get_word_data(response: aiohttp.ClientResponse) -> dict:
    """
    Function to get word data
    """
    output = {
        "en": {},
        "ru": {}
    }
    data = await response.json()

    word = data[0]

    output['en']['text'] = word['text']
    output['en']['transcription'] = word['meanings'][0]['transcription']
    output['en']['part_of_speech'] = word['meanings'][0]['partOfSpeechCode']
    output['en']['sound'] = 'https://vimbox-tts.skyeng.ru/api/v1/tts?text={}&lang=en&voice=male_2'.format(output["en"])

    output['ru']['text'] = word['meanings'][0]['translation']['text']
    output['ru']['image'] = word['meanings'][0]['imageUrl'].removeprefix('//')
    output['ru']['sound'] = 'https://vimbox-tts.skyeng.ru/api/v1/tts?text={}&lang=ru&voice=male_2'.format(
        output["ru"]["text"])

    return output


async def translate_word(word: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(
                get_url(word)) as resp:
            try:
                result.append(await get_word_data(resp))

            except IndexError:
                logger.error(f"[!] Word {word} not found")
            logger.success(f"[#] Translated {len(result)}/{len(words_list)} words)")


async def main():
    tasks = []
    for word in words_list:
        tasks.append(translate_word(word))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    result = []
    asyncio.run(main())
    json.dump(result, open('words.json', 'w', encoding='utf-8'), ensure_ascii=False)
