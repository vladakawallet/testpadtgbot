#import aiogram
from typing import Any, Awaitable, Callable, Dict
from aiogram import types, BaseMiddleware
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram import Bot
import config
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
#import asyncio
#from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram import F
import random
from aiogram.types import FSInputFile, Message
import os
import psycopg2 as ps
from psycopg2 import extras, errors
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from languages import LANGUAGES
import keyboards
import asyncpg
from urllib.parse import quote
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
import asyncio

#DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?async_fallback=True'

DATABASE_URL = f'postgresql://{quote(DB_USER)}:{quote(DB_PASS)}@{quote(DB_HOST)}:{quote(DB_PORT)}/{quote(DB_NAME)}'
 
# DATABASE_URL = f'postgresql://postgres:{password}@localhost:5432/testbase'

# db = ps.connect('postgresql://postgres:postgres@localhost:5432/testbase')
# mycursor = db.cursor()

db = ps.connect(DATABASE_URL)
mycursor = db.cursor()

selected_language = 'en'

bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class Start(StatesGroup):
    language = State()
    username = State()

class Learn(StatesGroup):
    start_learn = State()
    ready = State()
    run_test = State()
    ready_or_not = State()
    run_second_test = State()

class Config(StatesGroup):
    set_language = State()
    set_username = State()

user_languages = {}

# **********START CMD**********


@dp.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    try:
        mycursor.execute("CREATE TABLE IF NOT EXISTS test (user_id VARCHAR(20) PRIMARY KEY, sel_language VARCHAR(2), username VARCHAR(15) DEFAULT 'None')")
        db.commit()
    except:
        await message.answer("Oops, something went wrong! Try again later🤗")
        return
    else:
        try:
            mycursor.execute("SELECT * FROM test WHERE user_id = %s", (user_id,))
            info = mycursor.fetchone()
            if info:
                try:
                    mycursor.execute("SELECT * FROM test WHERE user_id = %s", (user_id,))
                    data = mycursor.fetchall()
                    await message.answer(LANGUAGES[data[0][1]]['primarykey_err'].format(username=data[0][2]), reply_markup=keyboards.help_kb, parse_mode=ParseMode.MARKDOWN)
                except:
                    await message.answer("Oops, something went wrong! Try again later🤗")
                    return
            else:
                await message.answer("Weclome to *TestPad* telegram-bot!", parse_mode=ParseMode.MARKDOWN)
                await message.answer("Choose your language🇪🇺", reply_markup=keyboards.language_keyboard)
                await state.set_state(Start.language)
        except:
            await message.answer("Oops, something went wrong! Try again later🤗")
            return
        

    
@dp.message(F.text == "Українська🇺🇦", Start.language)
async def set_ukr(message: types.Message, state: FSMContext):
    global user_languages
    selected_language = "uk"
    user_id = str(message.from_user.id)
    user_languages[user_id] = "uk"
    try:
        mycursor.execute("INSERT INTO test(user_id, sel_language) VALUES (%s, %s)", (user_id, selected_language))
        db.commit()
    except:
        await message.answer(LANGUAGES[selected_language]['insert_error'])
    await message.answer("Встановлена українська мова🇺🇦")
    await state.clear()
    await message.answer(LANGUAGES[user_languages.get(user_id)]['username'])
    await state.set_state(Start.username)

@dp.message(F.text == "English🇬🇧", Start.language)
async def set_eng(message: types.Message, state: FSMContext):
    global user_languages
    selected_language = "en"
    user_id = str(message.from_user.id)
    user_languages[user_id] = "en"
    try:
        mycursor.execute("INSERT INTO test(user_id, sel_language) VALUES (%s, %s)", (user_id, selected_language))
        db.commit()
    except:
        await message.answer(LANGUAGES[selected_language]['insert_error'])
    await message.answer("English language is set🇬🇧")
    await state.clear()
    await message.answer(LANGUAGES[user_languages.get(user_id)]['username'])
    await state.set_state(Start.username)
    



@dp.message(Start.username)
async def get_username(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    global user_languages
    username = message.text
    await message.answer(LANGUAGES[user_languages.get(user_id)]['greeting'].format(username=username),
                          parse_mode=ParseMode.MARKDOWN, reply_markup=keyboards.help_btn)
    try:
        mycursor.execute("UPDATE test SET username = %s WHERE user_id = %s", (username, user_id))
        db.commit()
    except:
        await message.answer(LANGUAGES[user_languages.get(user_id)['insert_error']])
    await state.clear()


# **********HELP CMD**********
@dp.message(F.text == 'Help🔫')
@dp.message(Command("help"))   
async def help_command(message: types.Message):
    user_id = str(message.from_user.id)
    try: 
        mycursor.execute("SELECT sel_language FROM test WHERE user_id = %s", (user_id,))
        language = mycursor.fetchall()
        user_languages[user_id] = str(language[0][0])
    except:
        await message.answer("Server disconnected. Try again later..." , reply_markup=keyboards.help_kb)
        return
    await message.answer(LANGUAGES[user_languages.get(user_id)]['help'], reply_markup=keyboards.help_kb)

@dp.message(F.text == "Cancel🚩")
@dp.message(F.text == "Скасувати🚩")
async def cancel_second_test(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    try: 
        mycursor.execute("SELECT sel_language FROM test WHERE user_id = %s", (user_id,))
        language = mycursor.fetchall()
        user_languages[user_id] = str(language[0][0])
    except:
        await message.answer("Server disconnected. Try again later..." , reply_markup=keyboards.help_kb)
        return
    user_data = await state.get_data()
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(LANGUAGES[user_languages.get(user_id)]['cancel_empty'], reply_markup=keyboards.help_kb)
    elif current_state == Learn.run_test:
        user_id = str(message.from_user.id)
        user_data = await state.get_data()
        vocabulary = user_data["vocabulary"]
        res1k = vocabulary
        await message.answer(LANGUAGES[user_languages.get(user_id)]['canceled_test'].format(res=res1k), reply_markup=keyboards.help_kb, parse_mode=ParseMode.MARKDOWN)
        await state.clear()
    elif current_state == Learn.run_second_test:
        user_id = str(message.from_user.id)
        user_data = await state.get_data()
        check = user_data["check"]
        res1k = '\n'.join([' '.join(i) for i in check])
        await message.answer(LANGUAGES[user_languages.get(user_id)]['canceled_test'].format(res=res1k), reply_markup=keyboards.help_kb, parse_mode=ParseMode.MARKDOWN)
        await state.clear()
        # mycursor.execute("TRUNCATE TABLE test2")
        # db.commit()
    else:
        await state.clear()
        await message.answer(LANGUAGES[user_languages.get(user_id)]['cancel'], reply_markup=keyboards.help_kb)


# *****INFORMATION BUTTON*****
@dp.message(F.text == "Inforamtion🗃")
@dp.message(Command("info"))
async def info_command(message: types.Message): 
    user_id = str(message.from_user.id)  
    try: 
        mycursor.execute("SELECT sel_language FROM test WHERE user_id = %s", (user_id,))
        language = mycursor.fetchall()
        user_languages[user_id] = str(language[0][0])
    except:
        await message.answer("Server disconnected. Try again later..." , reply_markup=keyboards.help_kb)
        return
    await message.answer(LANGUAGES[user_languages.get(user_id)]['information'], reply_markup=keyboards.help_kb, parse_mode=ParseMode.HTML)
# *****CONFIG BUTTON******
@dp.message(F.text == "Config⚙")
@dp.message(Command("config"))
async def config_command(message: types.Message):
    user_id = str(message.from_user.id)
    try: 
        mycursor.execute("SELECT sel_language FROM test WHERE user_id = %s", (user_id,))
        language = mycursor.fetchall()
        user_languages[user_id] = str(language[0][0])
    except:
        await message.answer("Server disconnected. Try again later..." , reply_markup=keyboards.help_kb)
        return
    if user_languages.get(user_id) == "en":
        await message.answer(LANGUAGES[user_languages.get(user_id)]['config'], parse_mode=ParseMode.MARKDOWN, reply_markup=keyboards.config_inline_kb)
    elif user_languages.get(user_id) == "uk":
        await message.answer(LANGUAGES[user_languages.get(user_id)]['config'], reply_markup=keyboards.config_inline_kb_ua)



@dp.message(F.text == "Language🇪🇺")
@dp.message(F.text == "Мова🇪🇺")
async def set_language(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    global user_languages
    await message.answer(LANGUAGES[user_languages.get(user_id)]['config_language'], parse_mode=ParseMode.MARKDOWN, reply_markup=keyboards.language_keyboard)
    await state.set_state(Config.set_language)
    

@dp.message(F.text == "Українська🇺🇦", Config.set_language)
async def ukr_language(message: types.Message, state: FSMContext):
    global user_languages
    user_id = str(message.from_user.id)
    selected_language = "uk"
    user_languages[user_id] = "uk"
    try:
        mycursor.execute("UPDATE test SET sel_language = %s WHERE user_id = %s", (selected_language, user_id))
        db.commit()
    except:
        await message.answer(LANGUAGES[selected_language]['insert_error'])
    await message.answer("Встановлена українська мова🇺🇦", reply_markup=keyboards.help_kb)
    await state.clear()
    


@dp.message(F.text == "English🇬🇧", Config.set_language)
async def eng_language(message: types.Message, state: FSMContext):
    global user_language
    user_id = str(message.from_user.id)
    selected_language = "en"
    user_languages[user_id] = "en"
    try:
        mycursor.execute("UPDATE test SET sel_language = %s WHERE user_id = %s", (selected_language, user_id))
        db.commit()
    except:
        await message.answer(LANGUAGES[selected_language]['insert_error'])
    await message.answer("English language is set🇬🇧", reply_markup=keyboards.help_kb)
    await state.clear()
    

@dp.message(F.text == "Username💻")
@dp.message(F.text == "Користувач💻")
async def set_username(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    if user_languages.get(user_id) == "en":
        await message.answer(LANGUAGES[user_languages.get(user_id)]['config_username'], reply_markup=keyboards.cancel_btn)
    elif user_languages.get(user_id) == "uk":
        await message.answer(LANGUAGES[user_languages.get(user_id)]['config_username'], reply_markup=keyboards.cancel_btn_ua)
    
    await state.set_state(Config.set_username)

@dp.message(Config.set_username)
async def new_username(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    username = message.text
    try:
        mycursor.execute("UPDATE test SET username = %s WHERE user_id = %s", (username, user_id))
    except:
        await message.answer(LANGUAGES[user_languages.get(user_id)]['insert_error'])
    await message.answer(LANGUAGES[user_languages.get(user_id)]['config_new_username'].format(username=username), parse_mode=ParseMode.MARKDOWN, reply_markup=keyboards.help_kb)
    await state.clear()


# *****TUTORIAL BUTTON*****
photo_path = FSInputFile(path='Pictures/instructoin3.jpg')
video_path = FSInputFile(path='Pictures/video.mp4')


@dp.message(F.text == 'Tutorial📝')
@dp.message(Command("tutor"))
async def tutorial_button(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    try: 
        mycursor.execute("SELECT sel_language FROM test WHERE user_id = %s", (user_id,))
        language = mycursor.fetchall()
        user_languages[user_id] = str(language[0][0])
    except:
        await message.answer("Server disconnected. Try again later..." , reply_markup=keyboards.help_kb)
        return
    if await state.get_state() is None:
        pass
    else:
        await state.clear()
    await message.answer_video(video=video_path, caption=LANGUAGES[user_languages.get(user_id)]['tutor_video'], parse_mode=ParseMode.MARKDOWN)
    await message.answer_photo(photo=photo_path, caption=LANGUAGES[user_languages.get(user_id)]['tutor_photo'], parse_mode=ParseMode.MARKDOWN, reply_markup=keyboards.help_kb)
# *****LEARN CMD**********

# Cancel handler

    
# Learn Button
@dp.message(F.text == 'Learn📚')
@dp.message(Command("learn"))
async def learn_button(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    try: 
        mycursor.execute("SELECT sel_language FROM test WHERE user_id = %s", (user_id,))
        language = mycursor.fetchall()
        user_languages[user_id] = str(language[0][0])
    except:
        await message.answer("Server disconnected. Try again later..." , reply_markup=keyboards.help_kb)
        return
    await state.set_state(Learn.start_learn)
    if user_languages.get(user_id) == 'en':
        await message.answer(LANGUAGES[user_languages.get(user_id)]['learn_dict_create'], parse_mode=ParseMode.MARKDOWN)
        await message.answer(LANGUAGES[user_languages.get(user_id)]['learn_pass_words'], reply_markup=keyboards.cancel_btn)
    elif user_languages.get(user_id) == 'uk':
        await message.answer(LANGUAGES[user_languages.get(user_id)]['learn_dict_create'], parse_mode=ParseMode.MARKDOWN)
        await message.answer(LANGUAGES[user_languages.get(user_id)]['learn_pass_words'],reply_markup=keyboards.cancel_btn_ua)




# Create dictionary
@dp.message(Learn.start_learn)
async def create_dictionary(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    global vocabulary
    string = message.text
    mycursor.execute("UPDATE test SET test_case = %s WHERE user_id = %s", (string, user_id))
    db.commit()
        # await message.answer(LANGUAGES[user_languages.get(user_id)]['insert_error'], reply_markup=keyboards.help_kb)
        # await state.clear()
    lines = string.split('\n')
    exceptions = 0
    for i in lines:
        i = i.split()
        if len(i) != 2:
            await message.answer(LANGUAGES[user_languages.get(user_id)]['learn_invalid_value'])
            await state.set_state(Learn.start_learn)
            exceptions += 1
        else:
            if exceptions == 0:
                if user_languages.get(user_id) == "en":
                    await message.answer(LANGUAGES[user_languages.get(user_id)]['complete_dict'], reply_markup=keyboards.ready_kb)
                else:
                    await message.answer(LANGUAGES[user_languages.get(user_id)]['complete_dict'], reply_markup=keyboards.ready_kb_ua)
                exceptions +=1
            await state.update_data(vocabulary=message.text)
            await state.set_state(Learn.ready)
    # user_words = await state.get_data()
    # dictionary = user_words["vocabulary"]
    
            # vocabulary[i[0]] = i[1]
            # for key, value in tuple(vocabulary.items()):
            #     pass
                # try:
                #     mycursor.execute("INSERT INTO test (test_key, test_value) VALUES (%s, %s)", (key, value))
                #     db.commit()
                # except:
                #     exceptions += 1

# Run test
@dp.message(F.text == "READY🎮", Learn.ready)
async def test_start(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    global global_result 
    vocabulary = {}
    global_result = []
    user_words = await state.get_data()
    dictionary = user_words["vocabulary"]
    lines = dictionary.split('\n')
    random.shuffle(lines)
    for i in lines:
        global_result.append(i.split())
    whole = len(global_result)
    score = len(global_result)
    check = []
    attempt = 0
    await state.update_data(attempt=attempt)
    await state.update_data(check=check)
    await state.update_data(whole=whole)
    await state.update_data(score=score)
    if user_languages[user_id] == "en":
        await message.answer(LANGUAGES[user_languages.get(user_id)]['learn_start'], reply_markup=keyboards.cancel_btn)
    if user_languages[user_id] == "uk":
        await message.answer(LANGUAGES[user_languages.get(user_id)]['learn_start'], reply_markup=keyboards.cancel_btn_ua)    
    await message.answer(f"*{global_result[0][0]}*", parse_mode=ParseMode.MARKDOWN)
    await state.set_state(Learn.run_test)



@dp.message(Learn.run_test)
async def test_process(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    await state.update_data(answer=message.text)
    user_data = await state.get_data()
    check = user_data["check"]
    whole = user_data["whole"]
    score = user_data["score"]
    answer = user_data["answer"]
    attempt = user_data["attempt"]
    if len(global_result) != 0:
        if answer == global_result[0][1] or answer.capitalize() == global_result[0][1]:
            await message.answer(LANGUAGES[user_languages.get(user_id)]['test_right'])
            attempt = 0
            await state.update_data(attempt=attempt)
            global_result.pop(0)
            if len(global_result) != 0:
                await message.answer(f"*{global_result[0][0]}*", parse_mode=ParseMode.MARKDOWN)
                await state.set_state(Learn.run_test)
            elif check == []:
                result = round((score/whole)*100)
                await message.answer(LANGUAGES[user_languages.get(user_id)]['right_test_result'].format(result=result),
                        reply_markup=keyboards.help_kb, parse_mode=ParseMode.MARKDOWN
                    )
                # mycursor.execute("TRUNCATE TABLE test")
                # db.commit()
                await state.clear()
            else:
                resik = round((score/whole)*100)
                lenka = len(check)
                if user_languages.get(user_id) == "en":
                    await message.answer(LANGUAGES[user_languages.get(user_id)]['wrong_test_result'].format(resik=resik, lenka=lenka),
                        reply_markup=keyboards.ready_or_not_kb, parse_mode=ParseMode.MARKDOWN)
                elif user_languages.get(user_id) == "uk":
                    await message.answer(LANGUAGES[user_languages.get(user_id)]['wrong_test_result'].format(resik=resik, lenka=lenka),
                        reply_markup=keyboards.ready_or_not_kb_ua, parse_mode=ParseMode.MARKDOWN)
                # mycursor.execute("TRUNCATE TABLE test")
                # db.commit()
                await state.set_state(Learn.ready_or_not)
        elif answer != global_result[0][1] or answer.capitalize() != global_result[0][1]:
            attempt += 1
            await state.update_data(attempt=attempt)
            user_data = await state.get_data()
            attempt = user_data["attempt"]
            if attempt == 0 or attempt == 1:
                await message.answer(LANGUAGES[user_languages.get(user_id)]['test_wrong'])
                await message.answer(f"*{global_result[0][0]}*", parse_mode=ParseMode.MARKDOWN)
            if attempt == 2:
                await message.answer(LANGUAGES[user_languages.get(user_id)]['test_wrong_second'].format(word=global_result[0][1]), parse_mode=ParseMode.MARKDOWN)
                check.append(global_result[0])
                attempt = 0
                score -= 1
                await state.update_data(attempt=attempt)
                await state.update_data(score=score)
                await state.update_data(check=check)
                global_result.pop(0)
                if len(global_result) != 0:
                    await message.answer(f"*{global_result[0][0]}*", parse_mode=ParseMode.MARKDOWN)
                    await state.set_state(Learn.run_test)
                else:
                    resuk = round((score/whole)*100)
                    lena = len(check)
                    if user_languages.get(user_id) == 'en':
                        await message.answer(LANGUAGES[user_languages.get(user_id)]['wrong_test_result'].format(resik=resuk, lenka=lena),
                                                reply_markup=keyboards.ready_or_not_kb, parse_mode=ParseMode.MARKDOWN)
                    elif user_languages.get(user_id) == 'ua':
                        await message.answer(LANGUAGES[user_languages.get(user_id)]['wrong_test_result'].format(resik=resuk, lenka=lena),
                                                reply_markup=keyboards.ready_or_not_kb_ua, parse_mode=ParseMode.MARKDOWN)
                    await state.set_state(Learn.ready_or_not)

@dp.message(F.text == "Yes💯",Learn.ready_or_not)
@dp.message(F.text == "Так💯", Learn.ready_or_not)
async def second_test_start(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = str(message.from_user.id)
    check = user_data["check"]
    if user_languages[user_id] == "en":
        await message.answer(LANGUAGES[user_languages.get(user_id)]['learn_start'], reply_markup=keyboards.cancel_btn)
    if user_languages[user_id] == "uk":
        await message.answer(LANGUAGES[user_languages.get(user_id)]['learn_start'], reply_markup=keyboards.cancel_btn_ua)
    await message.answer(f"*{check[0][0]}*", parse_mode=ParseMode.MARKDOWN)
    await state.set_state(Learn.run_second_test)

@dp.message(F.text == "No✖️", Learn.ready_or_not)
@dp.message(F.text == "Ні✖️", Learn.ready_or_not)
async def second_test_break(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_data = await state.get_data()
    check = user_data["check"]
    res1k = '\n'.join([' '.join(i) for i in check])
    await message.answer(LANGUAGES[user_languages.get(user_id)]['canceled_test'].format(res=res1k), reply_markup=keyboards.help_kb, parse_mode=ParseMode.MARKDOWN)
    await state.clear()


@dp.message(Learn.run_second_test)
async def second_test_process(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    await state.update_data(answer=message.text)
    user_data = await state.get_data()
    check = user_data["check"]
    answer = user_data["answer"]
    if len(check) != 0:
        if answer == check[0][1] or answer.capitalize() == check[0][1]:
            check.pop(0)
            await state.update_data(check=check)
            if len(check) == 0:
                await message.answer(LANGUAGES[user_languages.get(user_id)]['second_test_complete'], parse_mode=ParseMode.MARKDOWN, reply_markup=keyboards.help_kb)
                # mycursor.execute("TRUNCATE TABLE test2")
                # db.commit()
                await state.clear()
            else:
                await message.answer(LANGUAGES[user_languages.get(user_id)]['test_right'])
                await message.answer(f"*{check[0][0]}*", parse_mode=ParseMode.MARKDOWN)
                await state.set_state(Learn.run_second_test)
        elif answer != check[0][1] or answer.capitalize() != check[0][1]:
            await message.answer(LANGUAGES[user_languages.get(user_id)]['test_wrong'])
            await message.answer(f"*{check[0][0]}*", parse_mode=ParseMode.MARKDOWN)
            await state.set_state(Learn.run_second_test)




HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
WEBHOOK_HOST = f'https://testpadtgbot-acf7a4085c54.herokuapp.com'
WEBHOOK_PATH = f'/{config.TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = os.environ.get("PORT", default=8080)

async def on_startup(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    

async def main():
    # dp.startup.register(on_startup)
    # app = web.Application()
    # webhook_handler = SimpleRequestHandler(
    #     dispatcher=dp,
    #     bot=bot,
    # )
    # webhook_handler.register(app, path=WEBHOOK_PATH)
    # setup_application(app, dp, bot=bot)
    # web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())