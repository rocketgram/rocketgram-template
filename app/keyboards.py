from mybot import router
from rocketgram import MessageType, ReplyKeyboard, ReplyKeyboardRemove
from rocketgram import context, commonfilters, ChatType, SendMessage


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/keyboard')
async def keyboard_command():
    """Shows how to create reply keyboard"""

    kb = ReplyKeyboard()
    kb.text("😃 Super").row()
    kb.text("🙃 Great").row()
    kb.text("🤨 Not bad").row()
    kb.text("😖 All bad").row()
    kb.text("/cancel")

    await SendMessage(context.user.id, '🔹 How are you feeling?', reply_markup=kb.render()).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/keyboard_location')
async def keyboard_location_command():
    """Shows how to create location button"""

    kb = ReplyKeyboard()
    kb.location("🗺 Send location").row()
    kb.text("/cancel")

    await SendMessage(context.user.id, '🔹 Send me your location.', reply_markup=kb.render()).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.message_type(MessageType.location)
async def got_location():
    """Reaction on location"""

    await SendMessage(context.user.id,
                      '🔹 Now i known where are you. 😄',
                      reply_markup=ReplyKeyboardRemove(),
                      reply_to_message_id=context.message.message_id).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/keyboard_contact')
async def keyboard_contact_command():
    """Shows how to create contact button"""

    kb = ReplyKeyboard()
    kb.contact("☎️ Send contact").row()
    kb.text("/cancel")

    await SendMessage(context.user.id, '🔹 Send me your contact.', reply_markup=kb.render()).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.message_type(MessageType.contact)
async def got_contact():
    """Reaction on contact"""

    await SendMessage(context.user.id,
                      '🔹 Now i known your phone. 😄',
                      reply_markup=ReplyKeyboardRemove(),
                      reply_to_message_id=context.message.message_id).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/cancel')
def cancel_command():
    """Removes current reply keyboard"""

    SendMessage(context.user.id, "🔹 What's next?", reply_markup=ReplyKeyboardRemove()).webhook()
