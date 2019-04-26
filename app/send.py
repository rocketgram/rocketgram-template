import os
from io import FileIO

from mybot import router
from rocketgram import InputFile, SendAudio, SendChatAction
from rocketgram import commonfilters, ChatType, ChatActionType
from rocketgram import context


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/send')
async def send():
    """Shows how to send files."""

    file = InputFile('music.mp3', 'audio/mpeg', FileIO(os.path.dirname(__file__) + '/music.mp3', 'rb'))

    await SendChatAction(context.chat().chat_id, ChatActionType.upload_document).send()

    await SendAudio(context.chat().chat_id, file).send()
