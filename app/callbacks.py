from mybot import router
from rocketgram import Context, commonfilters, ChatType
from rocketgram import InlineKeyboard


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/simple_inline_keyboard')
async def simple_inline_keyboard(ctx: Context):
    """Shows how to create inline keyboard."""

    kb = InlineKeyboard()
    kb.callback("😃 Super", 'simple 1').row()
    kb.callback("🙃 Great", 'simple 2').row()
    kb.callback("🤨 Not bad", 'simple 3').row()
    kb.callback("😖 All bad", 'simple 4').row()
    kb.callback("❌ Close", 'simple close')

    await ctx.bot.send_message(ctx.update.message.user.user_id,
                               '🔹 How are you filling?',
                               reply_markup=kb.render())


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('simple')
async def reaction_on_simple_keyboard(ctx: Context):
    """Reaction on simple keyboard."""

    variant = ctx.update.callback_query.data.split()[1]

    if variant == 'close':
        await ctx.bot.answer_callback_query(ctx.update.callback_query.query_id)
        await ctx.bot.delete_message(ctx.update.callback_query.message.chat.chat_id,
                                     ctx.update.callback_query.message.message_id)
        return

    answers = {
        '1': '🔹 Super, Ok!',
        '2': '🔹 Great, Ok!',
        '3': '🔹 Ok!',
        '4': '🔹 Sad!',

    }

    msg = answers[variant]

    await ctx.bot.answer_callback_query(ctx.update.callback_query.query_id, msg, show_alert=True)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/arranged_inline_keyboard')
async def arranged_simple_inline_keyboard(ctx: Context):
    """Shows how to arrange inline keyboard."""

    kb = InlineKeyboard()

    for i in range(30):
        kb.callback("%s" % i, 'arranged %s' % i)

    kb.callback("❌ Close", 'arranged close')

    kb.arrange_simple(5)

    await ctx.bot.send_message(ctx.update.message.user.user_id,
                               '🔹 Select number.',
                               reply_markup=kb.render())


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('arranged')
async def reaction_on_simple_keyboard(ctx: Context):
    """Reaction on arranged simple keyboard"""

    variant = ctx.update.callback_query.data.split()[1]

    if variant == 'close':
        await ctx.bot.answer_callback_query(ctx.update.callback_query.query_id)
        await ctx.bot.delete_message(ctx.update.callback_query.message.chat.chat_id,
                                     ctx.update.callback_query.message.message_id)
        return

    msg = '🔹 Selected: %s' % variant

    await ctx.bot.answer_callback_query(ctx.update.callback_query.query_id, msg)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/arranged_scheme_inline_keyboard')
async def arranged_simple_inline_keyboard(ctx: Context):
    """Shows how to arrange inline keyboard by scheme."""

    kb = InlineKeyboard()

    kb.callback("⏪ Prev", 'scheme prev')
    kb.callback("✅ Do!", 'scheme do')
    kb.callback("Next ⏩", 'scheme next')

    for i in range(60):
        kb.callback("%s" % i, 'scheme %s' % i)

    kb.callback("❌ Close", 'scheme close')

    kb.arrange_scheme(3, 6, 1)

    await ctx.bot.send_message(ctx.update.message.user.user_id,
                               '🔹 Select number.',
                               reply_markup=kb.render())


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('scheme')
async def reaction_on_simple_keyboard(ctx: Context):
    """Reaction on arranged simple keyboard."""

    variant = ctx.update.callback_query.data.split()[1]

    if variant == 'close':
        await ctx.bot.answer_callback_query(ctx.update.callback_query.query_id)
        await ctx.bot.delete_message(ctx.update.callback_query.message.chat.chat_id,
                                     ctx.update.callback_query.message.message_id)
        return

    if variant == 'do':
        await ctx.bot.answer_callback_query(ctx.update.callback_query.query_id, '🔹 Doing something', show_alert=True)
        return

    if variant == 'prev':
        await ctx.bot.answer_callback_query(ctx.update.callback_query.query_id, '🔹 Showing previous page',
                                            show_alert=True)
        return

    if variant == 'next':
        await ctx.bot.answer_callback_query(ctx.update.callback_query.query_id, '🔹 Showing next page',
                                            show_alert=True)
        return

    msg = '🔹 Selected: %s' % variant

    await ctx.bot.answer_callback_query(ctx.update.callback_query.query_id, msg)
