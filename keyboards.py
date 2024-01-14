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
config_inline_kb = ReplyKeyboardMarkup(keyboard=config_kb_buttons, resize_keyboard=True)
config_inline_kb_ua = ReplyKeyboardMarkup(keyboard=config_kb_buttons_ua, resize_keyboard=True)


language_buttons = [
    [KeyboardButton(text="Українська🇺🇦"), KeyboardButton(text="English🇬🇧")]
]
language_keyboard = ReplyKeyboardMarkup(keyboard=language_buttons, resize_keyboard=True, one_time_keyboard=True)



cancel_btn = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Cancel🚩")]], resize_keyboard=True, one_time_keyboard=True)
cancel_btn_ua = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Скасувати🚩")]], resize_keyboard=True, one_time_keyboard=True)

#**READY**

ready_btns = [[KeyboardButton(text="READY🎮"), KeyboardButton(text="Cancel🚩")]]
ready_btns_ua = [[KeyboardButton(text="READY🎮"), KeyboardButton(text="Скасувати🚩")]]

ready_kb = ReplyKeyboardMarkup(keyboard=ready_btns, resize_keyboard=True, one_time_keyboard=True)
ready_kb_ua = ReplyKeyboardMarkup(keyboard=ready_btns_ua, resize_keyboard=True, one_time_keyboard=True)

ready_or_not_btns = [
    [KeyboardButton(text="Yes💯"), KeyboardButton(text="No✖️")]
]
ready_or_not_btns_ua = [
    [KeyboardButton(text="Так💯"), KeyboardButton(text="Ні✖️")]
]
ready_or_not_kb = ReplyKeyboardMarkup(keyboard=ready_or_not_btns, resize_keyboard=True)
ready_or_not_kb_ua = ReplyKeyboardMarkup(keyboard=ready_or_not_btns_ua, resize_keyboard=True)
