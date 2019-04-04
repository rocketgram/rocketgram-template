from mybot import router
from rocketgram import Context, commonfilters, ChatType, SendMessage
from rocketgram import MessageType, ReplyKeyboard, ReplyKeyboardRemove


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/keyboard')
async def keyboard_command(ctx: Context):
    """Shows how to create reply keyboard"""

    kb = ReplyKeyboard()
    kb.text("😃 Super").row()
    kb.text("🙃 Great").row()
    kb.text("🤨 Not bad").row()
    kb.text("😖 All bad").row()
    kb.text("/cancel")

    await ctx.bot.send_message(ctx.update.message.user.user_id,
                               '🔹 How are you filling?',
                               reply_markup=kb.render())


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/keyboard_location')
async def keyboard_location_command(ctx: Context):
    """Shows how to create location button"""

    kb = ReplyKeyboard()
    kb.location("🗺 Send location").row()
    kb.text("/cancel")

    await ctx.bot.send_message(ctx.update.message.user.user_id,
                               '🔹 Send me your location.',
                               reply_markup=kb.render())


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.message_type(MessageType.location)
async def got_location(ctx: Context):
    """Reaction on location"""

    await ctx.bot.send_message(ctx.update.message.user.user_id,
                               '🔹 Now i known where are you. 😄',
                               reply_markup=ReplyKeyboardRemove(),
                               reply_to_message_id=ctx.update.message.message_id)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/keyboard_contact')
async def keyboard_contact_command(ctx: Context):
    """Shows how to create contact button"""

    kb = ReplyKeyboard()
    kb.contact("☎️ Send contact").row()
    kb.text("/cancel")

    await ctx.bot.send_message(ctx.update.message.user.user_id,
                               '🔹 Send me your contact.',
                               reply_markup=kb.render())


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.message_type(MessageType.contact)
async def got_contact(ctx: Context):
    """Reaction on contact"""

    await ctx.bot.send_message(ctx.update.message.user.user_id,
                               '🔹 Now i known your phone. 😄',
                               reply_markup=ReplyKeyboardRemove(),
                               reply_to_message_id=ctx.update.message.message_id)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/cancel')
def cancel_command(ctx: Context):
    """Removes current reply keyboard"""

    whr = SendMessage(ctx.update.message.user.user_id,
                      "🔹 What next?",
                      reply_markup=ReplyKeyboardRemove())

    ctx.webhook_request(whr)
