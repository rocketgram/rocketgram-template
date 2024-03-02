import json
from hashlib import md5

import aiohttp

from mybot import router
from rocketgram import InlineKeyboard, AnswerInlineQuery, InlineQueryResultPhoto
from rocketgram import InlineQueryResultArticle, InputTextMessageContent
from rocketgram import SendMessage, LinkPreviewOptions
from rocketgram import commonfilters, ChatType, UpdateType, priority
from rocketgram import context


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/inline')
async def inline():
    """Shows how to use inline."""

    kb = InlineKeyboard()

    kb.inline("🏞 Get some photos", switch_inline_query='#photos').row()
    kb.inline("⁉️ Ask wikipedia", switch_inline_query="").row()

    await SendMessage(
        context.user.id,
        '🔹 Demo for inline mode.\n'
        '\n'
        'Photos for demo taken from this site:\n'
        'https://unsplash.com/creative-commons-images',
        link_preview_options=LinkPreviewOptions(
            is_disabled=True,
        ),
        reply_markup=kb.render(),
    ).send()


@router.handler
@commonfilters.update_type(UpdateType.inline_query)
@commonfilters.inline('#photo')
def inline_photo():
    """Shows how to send a photo though inline."""

    photos = [
        InlineQueryResultPhoto('1', 'https://telegra.ph/file/a225c61d9354bb0fc1241.jpg',
                               'https://telegra.ph/file/f9023fd8e7fc222ab33f1.jpg'),
        InlineQueryResultPhoto('2', 'https://telegra.ph/file/64cf1343413cdc9f5256e.jpg',
                               'https://telegra.ph/file/581a6262d4a2513370d02.jpg'),
        InlineQueryResultPhoto('3', 'https://telegra.ph/file/46b85c82aa644ed3db1f5.jpg',
                               'https://telegra.ph/file/231a77c904870951f0d19.jpg'),
        InlineQueryResultPhoto('4', 'https://telegra.ph/file/bf6dd32105d795f4d8c84.jpg',
                               'https://telegra.ph/file/64696eb4513e9f6c1ca9f.jpg'),
        InlineQueryResultPhoto('5', 'https://telegra.ph/file/898227042e0021df169d4.jpg',
                               'https://telegra.ph/file/84bdc622437d376e718c5.jpg'),
    ]

    AnswerInlineQuery(context.inline.id, photos).webhook()


@router.handler
@commonfilters.update_type(UpdateType.inline_query)
@priority(1024 + 128)
async def duckduckgo():
    """Produces simple wikipedia search."""

    # This is a little hack to avoid create own aiohttp session
    # never don't do like this ;)
    session: aiohttp.ClientSession = context.bot.connector._session

    params = {
        'action': 'opensearch',
        'search': context.inline.query,
    }
    try:
        response = await session.get('https://en.wikipedia.org/w/api.php', params=params)
        result = json.loads(await response.text())

        articles = []

        for idx in range(len(result[2])):
            text = f"{result[2][idx]}\n\n{result[3][idx]}"
            text_hash = md5(text.encode()).hexdigest()

            article = InlineQueryResultArticle(
                id=text_hash,
                title=result[1][idx],
                input_message_content=InputTextMessageContent(message_text=text),
                description=result[2][idx]
            )
            articles.append(article)

        AnswerInlineQuery(context.inline.id, articles).webhook()
    except (json.decoder.JSONDecodeError, aiohttp.ClientConnectorError):
        pass


@router.handler
@commonfilters.update_type(UpdateType.chosen_inline_result)
async def chosen():
    """Does nothing."""
    pass
