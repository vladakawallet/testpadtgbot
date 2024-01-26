from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

#*****HELP KEYBOARD*****
help_kb = [
    [KeyboardButton(text="Learn📚")],
    [KeyboardButton(text="Tutorial📝"), KeyboardButton(text="Help🔫")],
    [KeyboardButton(text="Config⚙"), KeyboardButton(text="Inforamtion🗃")]
]
help_kb = ReplyKeyboardMarkup(keyboard=help_kb, resize_keyboard=True)
help_btn = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Help🔫")]], resize_keyboard=True, one_time_keyboard=True)

#*****CONFIG KEYBOARD*****
config_kb_buttons = [[KeyboardButton(text="Username💻"), KeyboardButton(text="Language🇪🇺")]]
config_kb_buttons_ua = [[KeyboardButton(text="Користувач💻"), KeyboardButton(text="Мова🇪🇺")]]
config_kb_buttons_de = [[KeyboardButton(text="Nutzer💻"), KeyboardButton(text="Sprache🇪🇺")]]

config_inline_kb = ReplyKeyboardMarkup(keyboard=config_kb_buttons, resize_keyboard=True)
config_inline_kb_ua = ReplyKeyboardMarkup(keyboard=config_kb_buttons_ua, resize_keyboard=True)
config_inline_kb_de = ReplyKeyboardMarkup(keyboard=config_kb_buttons_de, resize_keyboard=True)

language_buttons = [
    [KeyboardButton(text="Українська🇺🇦"), KeyboardButton(text="English🇬🇧"), KeyboardButton(text="Deutsch🇩🇪")]
]
language_keyboard = ReplyKeyboardMarkup(keyboard=language_buttons, resize_keyboard=True, one_time_keyboard=True)

ready_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="READY🎮", callback_data="ready")]])

cancel_test_btn = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Exit🚩")]], resize_keyboard=True, one_time_keyboard=True)
cancel_test_btn_ua = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Завершити🚩")]], resize_keyboard=True, one_time_keyboard=True)
cancel_test_btn_de = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Verlassen🚩")]], resize_keyboard=True, one_time_keyboard=True)

cancel_btn = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Cancel🚩")]], resize_keyboard=True, one_time_keyboard=True)
cancel_btn_ua = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Скасувати🚩")]], resize_keyboard=True, one_time_keyboard=True)
cancel_btn_de = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Abbrechen🚩")]], resize_keyboard=True, one_time_keyboard=True)

#**READY**
ready_btns = [[KeyboardButton(text="READY🎮"), KeyboardButton(text="Cancel🚩")]]
ready_btns_ua = [[KeyboardButton(text="READY🎮"), KeyboardButton(text="Скасувати🚩")]]
ready_btns_de = [[KeyboardButton(text="READY🎮"), KeyboardButton(text="Abbrechen🚩")]]

ready_kb = ReplyKeyboardMarkup(keyboard=ready_btns, resize_keyboard=True, one_time_keyboard=True)
ready_kb_ua = ReplyKeyboardMarkup(keyboard=ready_btns_ua, resize_keyboard=True, one_time_keyboard=True)
ready_kb_de = ReplyKeyboardMarkup(keyboard=ready_btns_de, resize_keyboard=True, one_time_keyboard=True)

KEYBOARDS = {
    'en': {
        'config': config_inline_kb,
        'cancel': cancel_btn,
        'ready': ready_kb,
        'cancel_test': cancel_test_btn
    },
    'uk': {
        'config': config_inline_kb_ua,
        'cancel': cancel_btn_ua,
        'ready': ready_kb_ua,
        'cancel_test': cancel_test_btn_ua
    }, 
    'de': {
        'config': config_inline_kb_de,
        'cancel': cancel_btn_de,
        'ready': ready_kb_de,
        'cancel_test': cancel_test_btn_de
    }
    
}

