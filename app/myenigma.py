import logging
from functools import lru_cache
from secrets import token_urlsafe

from enigma.machine import KEYBOARD_CHARS, EnigmaMachine
from enigma.rotors.data import REFLECTORS, ROTORS
from munch import Munch

from mybot import router
from rocketgram import Bot, Context, commonfilters, ChatType
from rocketgram import InlineKeyboard, SendMessage, AnswerCallbackQuery

# Added one more reflector for compatibility to Android App
REFLECTORS['A'] = 'EJMZALYXVBWFCRQUONTSPIKHGD'

LETTERS_QWERTY = 'QWERTUIOASDFGHJKPYCVBNMLXZ'

MSG = Munch()
MSG.setup = """\
{setting}

<b>[{reflector}] {rotors}</b> / <b>{rings}</b>
<b>{plugboard}</b>
<b>{idisplay}</b>"""

MSG.setup_rotors = "Machine <b>rotors</b> setting:"
MSG.setup_rings = "Machine <b>rings</b> setting:"
MSG.setup_plugboard = "Machine <b>plugboard</b> setting:"
MSG.setup_display = "Machine <b>display</b> setting:"

MSG.enigma = """\
<b>{display}</b>
<code>{input}</code>
<code>{output}</code>

Machine initial settings:
<b>[{reflector}] {rotors}</b> / <b>{rings}</b>
<b>{plugboard}</b>
<b>{idisplay}</b>"""

MSG.plugboard_empty = "Plugboard empty"
MSG.expired = "Message is expired! Create new one!"
MSG.plugboard_error = "Plugboard must contains pairs of unique letters."

logger = logging.getLogger('enigma')


@router.on_init
def init(bot: Bot):
    bot.globals.enigmas = dict()


@lru_cache(128)
def enigma_kb(estat_id, cmd='enigma', pb=''):
    kb = InlineKeyboard()

    for c in LETTERS_QWERTY[:-2]:
        ch = c if c not in pb else '*'
        kb.callback(ch, f'{cmd} {estat_id} letter {c}')

    if cmd == 'enigma-plugboard':
        kb.callback('✖️ DEL', f'{cmd} {estat_id} del none')
    if cmd == 'enigma':
        kb.callback('⏪ SET', f'{cmd} {estat_id} set none')

    for c in LETTERS_QWERTY[-2:]:
        ch = c if c not in pb else '*'
        kb.callback(ch, f'{cmd} {estat_id} letter {c}')

    if cmd == 'enigma-display':
        kb.callback('RUN ▶️', f'{cmd} {estat_id} run none')
    elif cmd != 'enigma':
        kb.callback('NEXT ▶️', f'{cmd} {estat_id} done none')

    return kb.arrange_simple(8).render()


def rotors_kb(estat_id):
    kb = InlineKeyboard()

    for r in ROTORS.keys():
        kb.callback(r, f'enigma-rotors {estat_id} rotor {r}')

    for r in sorted(REFLECTORS.keys()):
        kb.callback(r, f'enigma-rotors {estat_id} reflector {r}')

    kb.callback('3-rotors', f'enigma-rotors {estat_id} 3rotors none')
    kb.callback('4-rotors', f'enigma-rotors {estat_id} 4rotors none')
    kb.callback('NEXT ▶️', f'enigma-rotors {estat_id} done none')

    return kb.arrange_simple(5).render()


# =========================================================================================
@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/enigma')
def enigma_cmd(ctx: Context):
    while True:
        new_id = token_urlsafe(8)
        if new_id not in ctx.bot.globals.enigmas:
            break

    estat = Munch()
    ctx.bot.globals.enigmas[new_id] = estat

    estat.input = ''
    estat.output = ''
    estat.rotors = 4
    estat.rotors_list = ['Beta', 'I', 'II', 'III']
    estat.rings_list = ['A', 'A', 'A', 'A']
    estat.reflector = 'C-Thin'
    estat.plugboard = []
    estat.display = ['A', 'A', 'A', 'A']

    m = MSG.setup.format(setting=MSG.setup_rotors,
                         display=' '.join(estat.display),
                         reflector=estat.reflector,
                         rotors=' '.join(estat.rotors_list),
                         rings=' '.join(estat.rings_list),
                         plugboard=' '.join(estat.plugboard) if len(
                             estat.plugboard) else MSG.plugboard_empty,
                         idisplay=' '.join(estat.display))

    whr = SendMessage(ctx.update.message.chat.chat_id, m, reply_markup=rotors_kb(new_id))
    ctx.webhook_request(whr)


# =========================================================================================
@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('enigma')
async def enigma_act(ctx: Context):
    estat_id, command, letter = ctx.update.callback_query.data.split()[1:]

    if estat_id not in ctx.bot.globals.enigmas:
        await ctx.bot.edit_message_reply_markup(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                                message_id=ctx.update.callback_query.message.message_id)
        whr = AnswerCallbackQuery(ctx.update.callback_query.query_id, MSG.expired)
        ctx.webhook_request(whr)
        return

    whr = AnswerCallbackQuery(ctx.update.callback_query.query_id)
    ctx.webhook_request(whr)

    estat = ctx.bot.globals.enigmas[estat_id]

    if command == 'set':
        estat.input = ''

        m = MSG.setup.format(setting=MSG.setup_display,
                             display=' '.join(estat.display),
                             reflector=estat.reflector,
                             rotors=' '.join(estat.rotors_list),
                             rings=' '.join(estat.rings_list),
                             plugboard=' '.join(estat.plugboard) if len(
                                 estat.plugboard) else MSG.plugboard_empty,
                             idisplay=' '.join(estat.display))

        kb = enigma_kb(estat_id, 'enigma-display')
        await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                        message_id=ctx.update.callback_query.message.message_id, text=m,
                                        reply_markup=kb)
        return

    machine = EnigmaMachine.from_key_sheet(
        rotors=estat.rotors_list,
        reflector=estat.reflector,
        ring_settings=' '.join(estat.rings_list),
        plugboard_settings=' '.join(estat.plugboard))

    machine.set_display(''.join(estat.display))

    estat.input += letter

    inp = ''.join([l if (n+1) % 5 else l+' ' for n, l in enumerate(estat.input)])
    out = ''.join([l if (n+1) % 5 else l+' ' for n, l in enumerate(machine.process_text(estat.input))])

    display = list(machine.get_display())
    if len(display) < 4 and estat.rotors == 4:
        display.insert(0, estat.display[0])
    display = ' '.join(display)

    m = MSG.enigma.format(display=display,
                          input=inp,
                          output=out,
                          reflector=estat.reflector,
                          rotors=' '.join(estat.rotors_list),
                          rings=' '.join(estat.rings_list),
                          plugboard=' '.join(estat.plugboard) if len(estat.plugboard) else MSG.plugboard_empty,
                          idisplay=' '.join(estat.display))

    await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                    message_id=ctx.update.callback_query.message.message_id, text=m,
                                    reply_markup=enigma_kb(estat_id))


# =========================================================================================
@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('enigma-display')
async def enigma_setup_display(ctx: Context):
    estat_id, command, letter = ctx.update.callback_query.data.split()[1:]

    if estat_id not in ctx.bot.globals.enigmas:
        await ctx.bot.edit_message_reply_markup(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                                message_id=ctx.update.callback_query.message.message_id)
        whr = AnswerCallbackQuery(ctx.update.callback_query.query_id, MSG.expired)
        ctx.webhook_request(whr)
        return

    whr = AnswerCallbackQuery(ctx.update.callback_query.query_id)
    ctx.webhook_request(whr)

    estat = ctx.bot.globals.enigmas[estat_id]

    if command == 'letter':
        if letter not in KEYBOARD_CHARS:
            return
        t = list(estat.display)
        estat.display.pop(0)
        estat.display.append(letter)
        if t == estat.display:
            return

    if command == 'run':
        m = MSG.enigma.format(input=estat.input,
                              display=' '.join(estat.display),
                              output=estat.output,
                              reflector=estat.reflector,
                              rotors=' '.join(estat.rotors_list),
                              rings=' '.join(estat.rings_list),
                              plugboard=' '.join(estat.plugboard) if len(estat.plugboard) else MSG.plugboard_empty,
                              idisplay=' '.join(estat.display))
        await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                        message_id=ctx.update.callback_query.message.message_id, text=m,
                                        reply_markup=enigma_kb(estat_id))
        return

    m = MSG.setup.format(setting=MSG.setup_display,
                         display=' '.join(estat.display),
                         reflector=estat.reflector,
                         rotors=' '.join(estat.rotors_list),
                         rings=' '.join(estat.rings_list),
                         plugboard=' '.join(estat.plugboard) if len(
                             estat.plugboard) else MSG.plugboard_empty,
                         idisplay=' '.join(estat.display))

    kb = enigma_kb(estat_id, 'enigma-display')
    await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                    message_id=ctx.update.callback_query.message.message_id,
                                    text=m, reply_markup=kb)


# =========================================================================================
@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('enigma-plugboard')
async def enigma_setup_plugboard(ctx: Context):
    estat_id, command, letter = ctx.update.callback_query.data.split()[1:]

    if estat_id not in ctx.bot.globals.enigmas:
        await ctx.bot.edit_message_reply_markup(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                                message_id=ctx.update.callback_query.message.message_id)
        whr = AnswerCallbackQuery(ctx.update.callback_query.query_id, MSG.expired)
        ctx.webhook_request(whr)
        return

    estat = ctx.bot.globals.enigmas[estat_id]

    if command == 'letter':
        if letter not in KEYBOARD_CHARS:
            return

        if letter in estat.plugboard:
            whr = AnswerCallbackQuery(ctx.update.callback_query.query_id, MSG.plugboard_error)
            ctx.webhook_request(whr)
            return

        if len(estat.plugboard) < 1:
            estat.plugboard.append('')

        if len(estat.plugboard[-1]) == 2:
            estat.plugboard.append('')

        estat.plugboard[-1] += letter

        if len(estat.plugboard) > 10:
            estat.plugboard.pop(0)

    if command == 'del':
        if len(estat.plugboard) < 1:
            return
        estat.plugboard.pop(-1)

    whr = AnswerCallbackQuery(ctx.update.callback_query.query_id)
    ctx.webhook_request(whr)

    if command == 'done':
        if len(estat.plugboard) > 0 and len(estat.plugboard[-1]) < 2:
            whr = AnswerCallbackQuery(ctx.update.callback_query.query_id, MSG.plugboard_error)
            ctx.webhook_request(whr)
            return

        m = MSG.setup.format(setting=MSG.setup_display,
                             display=' '.join(estat.display),
                             reflector=estat.reflector,
                             rotors=' '.join(estat.rotors_list),
                             rings=' '.join(estat.rings_list),
                             plugboard=' '.join(estat.plugboard) if len(
                                 estat.plugboard) else MSG.plugboard_empty,
                             idisplay=' '.join(estat.display))

        kb = enigma_kb(estat_id, 'enigma-display')
        await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                        message_id=ctx.update.callback_query.message.message_id,
                                        text=m, reply_markup=kb)
        return

    m = MSG.setup.format(setting=MSG.setup_plugboard,
                         display=' '.join(estat.display),
                         reflector=estat.reflector,
                         rotors=' '.join(estat.rotors_list),
                         rings=' '.join(estat.rings_list),
                         plugboard=' '.join(estat.plugboard) if len(
                             estat.plugboard) else MSG.plugboard_empty,
                         idisplay=' '.join(estat.display))

    kb = enigma_kb(estat_id, 'enigma-plugboard', ''.join(estat.plugboard))
    await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                    message_id=ctx.update.callback_query.message.message_id, text=m, reply_markup=kb)


# =========================================================================================
@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('enigma-rings')
async def enigma_setup_rings(ctx: Context):
    estat_id, command, letter = ctx.update.callback_query.data.split()[1:]

    if estat_id not in ctx.bot.globals.enigmas:
        await ctx.bot.edit_message_reply_markup(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                                message_id=ctx.update.callback_query.message.message_id)
        whr = AnswerCallbackQuery(ctx.update.callback_query.query_id, MSG.expired)
        ctx.webhook_request(whr)
        return

    whr = AnswerCallbackQuery(ctx.update.callback_query.query_id)
    ctx.webhook_request(whr)

    estat = ctx.bot.globals.enigmas[estat_id]

    if command == 'letter':
        if letter not in KEYBOARD_CHARS:
            return
        t = list(estat.rings_list)
        estat.rings_list.pop(0)
        estat.rings_list.append(letter)
        if t == estat.rings_list:
            return

    if command == 'done':
        m = MSG.setup.format(setting=MSG.setup_plugboard,
                             display=' '.join(estat.display),
                             reflector=estat.reflector,
                             rotors=' '.join(estat.rotors_list),
                             rings=' '.join(estat.rings_list),
                             plugboard=' '.join(estat.plugboard) if len(
                                 estat.plugboard) else MSG.plugboard_empty,
                             idisplay=' '.join(estat.display))

        kb = enigma_kb(estat_id, 'enigma-plugboard')
        await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                        message_id=ctx.update.callback_query.message.message_id,
                                        text=m, reply_markup=kb)
        return

    m = MSG.setup.format(setting=MSG.setup_rings,
                         display=' '.join(estat.display),
                         reflector=estat.reflector,
                         rotors=' '.join(estat.rotors_list),
                         rings=' '.join(estat.rings_list),
                         plugboard=' '.join(estat.plugboard) if len(
                             estat.plugboard) else MSG.plugboard_empty,
                         idisplay=' '.join(estat.display))

    kb = enigma_kb(estat_id, 'enigma-rings')
    await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                    message_id=ctx.update.callback_query.message.message_id,
                                    text=m, reply_markup=kb)


# =========================================================================================
@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('enigma-rotors')
async def enigma_setup_rotors(ctx: Context):
    estat_id, command, letter = ctx.update.callback_query.data.split()[1:]

    if estat_id not in ctx.bot.globals.enigmas:
        await ctx.bot.edit_message_reply_markup(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                                message_id=ctx.update.callback_query.message.message_id)
        whr = AnswerCallbackQuery(ctx.update.callback_query.query_id, MSG.expired)
        ctx.webhook_request(whr)
        return

    whr = AnswerCallbackQuery(ctx.update.callback_query.query_id)
    ctx.webhook_request(whr)

    estat = ctx.bot.globals.enigmas[estat_id]

    if command == 'rotor':
        if letter not in ROTORS.keys():
            return
        t = list(estat.rotors_list)
        estat.rotors_list.pop(0)
        estat.rotors_list.append(letter)
        if t == estat.rotors_list:
            return

    if command == 'reflector':
        if letter not in REFLECTORS.keys():
            return
        if letter == estat.reflector:
            return
        estat.reflector = letter

    if command == '3rotors':
        if estat.rotors == 3:
            return
        estat.rotors = 3
        if len(estat.rotors_list) != 3:
            estat.rotors_list.pop(0)
            estat.rings_list = ['A', 'A', 'A']
            estat.display = ['A', 'A', 'A']

    if command == '4rotors':
        if estat.rotors == 4:
            return
        estat.rotors = 4
        if len(estat.rotors_list) != 4:
            estat.rotors_list.insert(0, 'I')
            estat.rings_list = ['A', 'A', 'A', 'A']
            estat.display = ['A', 'A', 'A', 'A']

    if command == 'done':
        m = MSG.setup.format(setting=MSG.setup_rings,
                             display=' '.join(estat.display),
                             reflector=estat.reflector,
                             rotors=' '.join(estat.rotors_list),
                             rings=' '.join(estat.rings_list),
                             plugboard=' '.join(estat.plugboard) if len(
                                 estat.plugboard) else MSG.plugboard_empty,
                             idisplay=' '.join(estat.display))

        kb = enigma_kb(estat_id, 'enigma-rings')
        await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                        message_id=ctx.update.callback_query.message.message_id,
                                        text=m, reply_markup=kb)
        return

    m = MSG.setup.format(setting=MSG.setup_rotors,
                         display=' '.join(estat.display),
                         reflector=estat.reflector,
                         rotors=' '.join(estat.rotors_list),
                         rings=' '.join(estat.rings_list),
                         plugboard=' '.join(estat.plugboard) if len(
                             estat.plugboard) else MSG.plugboard_empty,
                         idisplay=' '.join(estat.display))

    await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                    message_id=ctx.update.callback_query.message.message_id, text=m,
                                    reply_markup=rotors_kb(estat_id))
