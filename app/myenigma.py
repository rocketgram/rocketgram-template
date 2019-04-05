import logging
from functools import lru_cache
from secrets import token_urlsafe

from enigma.machine import EnigmaMachine, KEYBOARD_CHARS
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

MSG.setup_rotors = "Machine rotors setting:"
MSG.setup_rings = "Machine rings setting:"
MSG.setup_plugboard = "Machine plugboard setting:"
MSG.setup_display = "Machine display setting:"

MSG.enigma = """\
<b>{display}</b>
<code>{input}</code>
<code>{output}</code>

Machine initial settings:
<b>[{reflector}] {rotors}</b> / <b>{rings}</b>
<b>{plugboard}</b>
<b>{idisplay}</b>"""

MSG.plugboard_empty = "Plugboard empty"
MSG.expiried = "Message is expired! Create new one!"
MSG.plugboard_error = "Plugboard must contains pairs of unique letters."

logger = logging.getLogger('enigma')


@router.on_init
def init(bot: Bot):
    bot.globals.enigmas = dict()


@lru_cache(128)
def enigma_kb(machine_id, cmd='enigma', pb=''):
    kb = InlineKeyboard()

    for c in LETTERS_QWERTY[:-2]:
        ch = c if c not in pb else '*'
        kb.callback(ch, f'{cmd} {machine_id} letter {c}')

    if cmd == 'enigma-plugboard':
        kb.callback('✖️ DEL', f'{cmd} {machine_id} del none')
    if cmd == 'enigma':
        kb.callback('⏪ SET', f'{cmd} {machine_id} set none')

    for c in LETTERS_QWERTY[-2:]:
        ch = c if c not in pb else '*'
        kb.callback(ch, f'{cmd} {machine_id} letter {c}')

    if cmd == 'enigma-display':
        kb.callback('RUN ▶️', f'{cmd} {machine_id} run none')
    elif cmd != 'enigma':
        kb.callback('NEXT ▶️', f'{cmd} {machine_id} done none')

    return kb.arrange_simple(8).render()


def rotors_kb(machine_id):
    kb = InlineKeyboard()

    for r in ROTORS.keys():
        kb.callback(r, f'enigma-rotors {machine_id} rotor {r}')

    for r in sorted(REFLECTORS.keys()):
        kb.callback(r, f'enigma-rotors {machine_id} reflector {r}')

    kb.callback('3-rotors', f'enigma-rotors {machine_id} 3rotors none')
    kb.callback('4-rotors', f'enigma-rotors {machine_id} 4rotors none')
    kb.callback('NEXT ▶️', f'enigma-rotors {machine_id} done none')

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

    machine = Munch()
    ctx.bot.globals.enigmas[new_id] = machine

    machine.input = ''
    machine.output = ''
    machine.rotors = 3
    machine.rotors_list = ['I', 'II', 'III']
    machine.rings_list = ['A', 'A', 'A']
    machine.reflector = 'A'
    machine.plugboard = []
    machine.display = ['A', 'A', 'A']
    machine.lcnt = 0

    m = MSG.setup.format(setting=MSG.setup_rotors,
                         display=' '.join(machine.display),
                         reflector=machine.reflector,
                         rotors=' '.join(machine.rotors_list),
                         rings=' '.join(machine.rings_list),
                         plugboard=' '.join(machine.plugboard) if len(
                             machine.plugboard) else MSG.plugboard_empty,
                         idisplay=' '.join(machine.display))

    whr = SendMessage(ctx.update.message.chat.chat_id, m, reply_markup=rotors_kb(new_id))
    ctx.webhook_request(whr)


# =========================================================================================
@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('enigma')
async def enigma_act(ctx: Context):
    machine_id, command, letter = ctx.update.callback_query.data.split()[1:]

    if machine_id not in ctx.bot.globals.enigmas:
        await ctx.bot.edit_message_reply_markup(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                                message_id=ctx.update.callback_query.message.message_id)
        whr = AnswerCallbackQuery(ctx.update.callback_query.query_id, MSG.expiried)
        ctx.webhook_request(whr)
        return

    whr = AnswerCallbackQuery(ctx.update.callback_query.query_id)
    ctx.webhook_request(whr)

    machine = ctx.bot.globals.enigmas[machine_id]

    display = ''

    if command == 'letter':
        lamp = machine.machine.key_press(letter)
        display = list(machine.machine.get_display())
        if len(display) < 4 and machine.rotors == 4:
            display.insert(0, machine.display[0])
        display = ' '.join(display)

        machine.input += letter
        machine.output += lamp
        machine.lcnt += 1

        if machine.lcnt >= 5:
            machine.input += ' '
            machine.output += ' '
            machine.lcnt = 0

        if len(machine.input) > 3800:
            machine.input = machine.input[-3800:]
            machine.output = machine.output[-3800:]

    if command == 'set':
        machine.input = ''
        machine.output = ''
        machine.lcnt = 0

        m = MSG.setup.format(setting=MSG.setup_display,
                             display=' '.join(machine.display),
                             reflector=machine.reflector,
                             rotors=' '.join(machine.rotors_list),
                             rings=' '.join(machine.rings_list),
                             plugboard=' '.join(machine.plugboard) if len(
                                 machine.plugboard) else MSG.plugboard_empty,
                             idisplay=' '.join(machine.display))

        kb = enigma_kb(machine_id, 'enigma-display')
        await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                        message_id=ctx.update.callback_query.message.message_id, text=m,
                                        reply_markup=kb)
        return

    m = MSG.enigma.format(input=machine.input,
                          display=display,
                          output=machine.output,
                          reflector=machine.reflector,
                          rotors=' '.join(machine.rotors_list),
                          rings=' '.join(machine.rings_list),
                          plugboard=' '.join(machine.plugboard) if len(machine.plugboard) else MSG.plugboard_empty,
                          idisplay=' '.join(machine.display))

    await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                    message_id=ctx.update.callback_query.message.message_id, text=m,
                                    reply_markup=enigma_kb(machine_id))


# =========================================================================================
@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('enigma-display')
async def enigma_setup_display(ctx: Context):
    machine_id, command, letter = ctx.update.callback_query.data.split()[1:]

    if machine_id not in ctx.bot.globals.enigmas:
        await ctx.bot.edit_message_reply_markup(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                                message_id=ctx.update.callback_query.message.message_id)
        whr = AnswerCallbackQuery(ctx.update.callback_query.query_id, MSG.expiried)
        ctx.webhook_request(whr)
        return

    whr = AnswerCallbackQuery(ctx.update.callback_query.query_id)
    ctx.webhook_request(whr)

    machine = ctx.bot.globals.enigmas[machine_id]

    if command == 'letter':
        if letter not in KEYBOARD_CHARS:
            return
        t = list(machine.display)
        machine.display.pop(0)
        machine.display.append(letter)
        if t == machine.display:
            return

    if command == 'run':
        machine.machine = EnigmaMachine.from_key_sheet(
            rotors=machine.rotors_list,
            reflector=machine.reflector,
            ring_settings=' '.join(machine.rings_list),
            plugboard_settings=' '.join(machine.plugboard))

        machine.machine.set_display(''.join(machine.display))

        m = MSG.enigma.format(input=machine.input,
                              display=' '.join(machine.display),
                              output=machine.output,
                              reflector=machine.reflector,
                              rotors=' '.join(machine.rotors_list),
                              rings=' '.join(machine.rings_list),
                              plugboard=' '.join(machine.plugboard) if len(machine.plugboard) else MSG.plugboard_empty,
                              idisplay=' '.join(machine.display))
        await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                        message_id=ctx.update.callback_query.message.message_id, text=m,
                                        reply_markup=enigma_kb(machine_id))
        return

    m = MSG.setup.format(setting=MSG.setup_display,
                         display=' '.join(machine.display),
                         reflector=machine.reflector,
                         rotors=' '.join(machine.rotors_list),
                         rings=' '.join(machine.rings_list),
                         plugboard=' '.join(machine.plugboard) if len(
                             machine.plugboard) else MSG.plugboard_empty,
                         idisplay=' '.join(machine.display))

    kb = enigma_kb(machine_id, 'enigma-display')
    await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                    message_id=ctx.update.callback_query.message.message_id,
                                    text=m, reply_markup=kb)


# =========================================================================================
@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('enigma-plugboard')
async def enigma_setup_plugboard(ctx: Context):
    machine_id, command, letter = ctx.update.callback_query.data.split()[1:]

    if machine_id not in ctx.bot.globals.enigmas:
        await ctx.bot.edit_message_reply_markup(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                                message_id=ctx.update.callback_query.message.message_id)
        whr = AnswerCallbackQuery(ctx.update.callback_query.query_id, MSG.expiried)
        ctx.webhook_request(whr)
        return

    machine = ctx.bot.globals.enigmas[machine_id]

    if command == 'letter':
        if letter not in KEYBOARD_CHARS:
            return

        l = ''.join(machine.plugboard)

        if letter in l:
            whr = AnswerCallbackQuery(ctx.update.callback_query.query_id, MSG.plugboard_error)
            ctx.webhook_request(whr)
            return

        if len(machine.plugboard) < 1:
            machine.plugboard.append('')

        if len(machine.plugboard[-1]) == 2:
            machine.plugboard.append('')

        machine.plugboard[-1] += letter

        if len(machine.plugboard) > 10:
            machine.plugboard.pop(0)

    if command == 'del':
        if len(machine.plugboard) < 1:
            return
        machine.plugboard.pop(-1)

    whr = AnswerCallbackQuery(ctx.update.callback_query.query_id)
    ctx.webhook_request(whr)

    if command == 'done':
        if len(machine.plugboard) > 0 and len(machine.plugboard[-1]) < 2:
            whr = AnswerCallbackQuery(ctx.update.callback_query.query_id, MSG.plugboard_error)
            ctx.webhook_request(whr)
            return

        m = MSG.setup.format(setting=MSG.setup_display,
                             display=' '.join(machine.display),
                             reflector=machine.reflector,
                             rotors=' '.join(machine.rotors_list),
                             rings=' '.join(machine.rings_list),
                             plugboard=' '.join(machine.plugboard) if len(
                                 machine.plugboard) else MSG.plugboard_empty,
                             idisplay=' '.join(machine.display))

        kb = enigma_kb(machine_id, 'enigma-display')
        await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                        message_id=ctx.update.callback_query.message.message_id,
                                        text=m, reply_markup=kb)
        return

    m = MSG.setup.format(setting=MSG.setup_plugboard,
                         display=' '.join(machine.display),
                         reflector=machine.reflector,
                         rotors=' '.join(machine.rotors_list),
                         rings=' '.join(machine.rings_list),
                         plugboard=' '.join(machine.plugboard) if len(
                             machine.plugboard) else MSG.plugboard_empty,
                         idisplay=' '.join(machine.display))

    kb = enigma_kb(machine_id, 'enigma-plugboard', ''.join(machine.plugboard))
    await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                    message_id=ctx.update.callback_query.message.message_id, text=m, reply_markup=kb)


# =========================================================================================
@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('enigma-rings')
async def enigma_setup_rings(ctx: Context):
    machine_id, command, letter = ctx.update.callback_query.data.split()[1:]

    if machine_id not in ctx.bot.globals.enigmas:
        await ctx.bot.edit_message_reply_markup(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                                message_id=ctx.update.callback_query.message.message_id)
        whr = AnswerCallbackQuery(ctx.update.callback_query.query_id, MSG.expiried)
        ctx.webhook_request(whr)
        return

    whr = AnswerCallbackQuery(ctx.update.callback_query.query_id)
    ctx.webhook_request(whr)

    machine = ctx.bot.globals.enigmas[machine_id]

    if command == 'letter':
        if letter not in KEYBOARD_CHARS:
            return
        t = list(machine.rings_list)
        machine.rings_list.pop(0)
        machine.rings_list.append(letter)
        if t == machine.rings_list:
            return

    if command == 'done':

        m = MSG.setup.format(setting=MSG.setup_plugboard,
                             display=' '.join(machine.display),
                             reflector=machine.reflector,
                             rotors=' '.join(machine.rotors_list),
                             rings=' '.join(machine.rings_list),
                             plugboard=' '.join(machine.plugboard) if len(
                                 machine.plugboard) else MSG.plugboard_empty,
                             idisplay=' '.join(machine.display))

        kb = enigma_kb(machine_id, 'enigma-plugboard')
        await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                        message_id=ctx.update.callback_query.message.message_id,
                                        text=m, reply_markup=kb)
        return

    m = MSG.setup.format(setting=MSG.setup_rings,
                         display=' '.join(machine.display),
                         reflector=machine.reflector,
                         rotors=' '.join(machine.rotors_list),
                         rings=' '.join(machine.rings_list),
                         plugboard=' '.join(machine.plugboard) if len(
                             machine.plugboard) else MSG.plugboard_empty,
                         idisplay=' '.join(machine.display))

    kb = enigma_kb(machine_id, 'enigma-rings')
    await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                    message_id=ctx.update.callback_query.message.message_id,
                                    text=m, reply_markup=kb)


# =========================================================================================
@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('enigma-rotors')
async def enigma_setup_rotors(ctx: Context):
    machine_id, command, letter = ctx.update.callback_query.data.split()[1:]

    if machine_id not in ctx.bot.globals.enigmas:
        await ctx.bot.edit_message_reply_markup(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                                message_id=ctx.update.callback_query.message.message_id)
        whr = AnswerCallbackQuery(ctx.update.callback_query.query_id, MSG.expiried)
        ctx.webhook_request(whr)
        return

    whr = AnswerCallbackQuery(ctx.update.callback_query.query_id)
    ctx.webhook_request(whr)

    machine = ctx.bot.globals.enigmas[machine_id]

    if command == 'rotor':
        if letter not in ROTORS.keys():
            return
        t = list(machine.rotors_list)
        machine.rotors_list.pop(0)
        machine.rotors_list.append(letter)
        if t == machine.rotors_list:
            return

    if command == 'reflector':
        if letter not in REFLECTORS.keys():
            return
        if letter == machine.reflector:
            return
        machine.reflector = letter

    if command == '3rotors':
        if machine.rotors == 3:
            return
        machine.rotors = 3
        if len(machine.rotors_list) != 3:
            machine.rotors_list.pop(0)
            machine.rings_list = ['A', 'A', 'A']
            machine.display = ['A', 'A', 'A']

    if command == '4rotors':
        if machine.rotors == 4:
            return
        machine.rotors = 4
        if len(machine.rotors_list) != 4:
            machine.rotors_list.insert(0, 'I')
            machine.rings_list = ['A', 'A', 'A', 'A']
            machine.display = ['A', 'A', 'A', 'A']

    if command == 'done':
        m = MSG.setup.format(setting=MSG.setup_rings,
                             display=' '.join(machine.display),
                             reflector=machine.reflector,
                             rotors=' '.join(machine.rotors_list),
                             rings=' '.join(machine.rings_list),
                             plugboard=' '.join(machine.plugboard) if len(
                                 machine.plugboard) else MSG.plugboard_empty,
                             idisplay=' '.join(machine.display))

        kb = enigma_kb(machine_id, 'enigma-rings')
        await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                        message_id=ctx.update.callback_query.message.message_id,
                                        text=m, reply_markup=kb)
        return

    m = MSG.setup.format(setting=MSG.setup_rotors,
                         display=' '.join(machine.display),
                         reflector=machine.reflector,
                         rotors=' '.join(machine.rotors_list),
                         rings=' '.join(machine.rings_list),
                         plugboard=' '.join(machine.plugboard) if len(
                             machine.plugboard) else MSG.plugboard_empty,
                         idisplay=' '.join(machine.display))

    await ctx.bot.edit_message_text(chat_id=ctx.update.callback_query.message.chat.chat_id,
                                    message_id=ctx.update.callback_query.message.message_id, text=m,
                                    reply_markup=rotors_kb(machine_id))
