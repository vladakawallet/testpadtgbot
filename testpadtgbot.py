#aiogram
from aiogram import Router, types, BaseMiddleware, Bot, F, BaseMiddleware
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.fsm.scene import SceneRegistry
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import FSInputFile, Message

#__aiogram webhook__
#from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
#from aiohttp import web

#sqlalchemy
from sqlalchemy import insert, select, update, exc
from models import User

#utils
from utils import TestScene
from database import async_session_factory, get_language

#other
import config
import random
import asyncio
import logging
import keyboards
import psycopg2 as ps
from cachetools import LRUCache
from keyboards import KEYBOARDS
from languages import LANGUAGES
from urllib.parse import quote
from typing import Any, Awaitable, Callable, Dict
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER


DATABASE_URL_ASYNC = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

#logging
logger = logging.getLogger('logger')

#middleware 
cache = LRUCache(maxsize=128)

class LanguageMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.language = ''
        

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id: int = event.from_user.id
        language: str = await self.query(user_id)
        data['language'] = language
        return await handler(event, data)

    async def query(self, user_id: int) -> Any:
        if cache.get(str(user_id)) is None:
            stmt = select(User.language).where(User.id == user_id)
            async with async_session_factory() as session:
                async with session.begin():
                    try: 
                        res = await session.execute(stmt)
                        language = res.scalar()
                    except Exception as e:
                        logger.error(f'An error occured on {user_id}: {e}')
                        return None
                    else:
                        cache[str(user_id)] = language
                        return language
        else: 
            return cache[str(user_id)]


#test scene
test_router = Router(name=__name__)
test_router.message.register(TestScene.as_handler(), Command("test"))
test_router.message.register(TestScene.as_handler(), F.text == 'READY🎮')


#main
main_router = Router(name=__name__)
main_router.message.middleware(LanguageMiddleware())

#fsm
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

        
# Another possible, but depricated way to receive the asyncronous session 
# async def get_async_session():
#     async with async_session_factory() as session:
#         yield session

# **********START CMD**********
@main_router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    stmt = select(User).where(User.id == user_id)
    async with async_session_factory() as session:
        async with session.begin(): 
            try:
                res = await session.execute(stmt)
                data = res.scalar()
                if data:
                    await message.answer(LANGUAGES[data.language]['existed_user'].format(username=data.username),
                                          reply_markup=keyboards.help_kb, parse_mode=ParseMode.MARKDOWN)
                else:
                    await message.answer("Weclome to *TestPad* telegram-bot!", parse_mode=ParseMode.MARKDOWN)
                    await message.answer("Choose your language🇪🇺", reply_markup=keyboards.language_keyboard)
                    await state.set_state(Start.language)         
            except Exception as e:
                logger.error(f'An error occured on {user_id}: {e}')
                await message.answer(LANGUAGES['en']['main_error'])
                return

#set ukr
@main_router.message(F.text == "Українська🇺🇦", Start.language)
async def set_ukr(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    stmt = insert(User).values(id=user_id, language='uk').returning(User.language)
    async with async_session_factory() as session:
        async with session.begin():
            try:
                res = await session.execute(stmt)
                language = res.scalar()
            except Exception as e:
                logger.error(f'An error occured on {user_id}: {e}')
                await message.answer(LANGUAGES['uk']['main_error'])
                return
            else:
                await message.answer("Встановлена українська мова🇺🇦")
                await state.clear()
                await message.answer(LANGUAGES[language]['start_username'])
                await state.set_state(Start.username)
                await state.update_data(language=language)

#set eng
@main_router.message(F.text == "English🇬🇧", Start.language)
async def set_ukr(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    stmt = insert(User).values(id=user_id, language='en').returning(User.language)
    async with async_session_factory() as session:
        async with session.begin():
            try:
                res = await session.execute(stmt)
                language = res.scalar()
            except Exception as e:
                logger.error(f'An error occured on {user_id}: {e}')
                await message.answer(LANGUAGES['en']['main_error'])
                return
            else:
                await message.answer("English language is set🇬🇧")
                await state.clear()
                await message.answer(LANGUAGES[language]['start_username'])
                await state.set_state(Start.username)

#set de
@main_router.message(F.text == "Deutsch🇩🇪", Start.language)
async def set_ukr(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    stmt = insert(User).values(id=user_id, language='de').returning(User.language)
    async with async_session_factory() as session:
        async with session.begin():
            try:
                res = await session.execute(stmt)
                language = res.scalar()
            except Exception as e:
                logger.error(f'An error occured on {user_id}: {e}')
                await message.answer(LANGUAGES['de']['main_error'])
                return
            else:
                await message.answer("Deutsche Sprache ist eingestellt🇩🇪")
                await state.clear()
                await message.answer(LANGUAGES[language]['start_username'])
                await state.set_state(Start.username)
                await state.update_data(language=language)

#username
@main_router.message(Start.username)
async def get_username(message: types.Message, state: FSMContext, language: str):
    user_id = int(message.from_user.id)
    username = message.text
    if language is None:
        try: 
            language = await get_language(user_id)
        except TypeError as e:
            logger.error(f'An error occured on {user_id}: {e}')
            await message.answer(LANGUAGES['en']['main_error'], reply_markup=keyboards.help_kb)
            return
    stmt = update(User).where(User.id == user_id).values(username=username)
    async with async_session_factory() as session:
        async with session.begin():
            try:
                await session.execute(stmt)
                await message.answer(LANGUAGES[language]['start_greeting'].format(username=username),
                        parse_mode=ParseMode.MARKDOWN, reply_markup=keyboards.help_btn)
            except exc.IntegrityError as e:  
                await message.answer(LANGUAGES[language]['integrity_error'].format(username=username), parse_mode=ParseMode.MARKDOWN)
                await message.answer(LANGUAGES[language]['start_username'])
                await state.set_state(Start.username)
            except Exception as e:
                if len(username) > 32:
                    await message.answer(LANGUAGES[language]['length_error'])
                    await message.answer(LANGUAGES[language]['start_username'])
                    await state.set_state(Start.username)
                else:
                    logger.error(f'An error occured on {user_id}: {e}')
                    await message.answer(LANGUAGES[language]['main_error'])
                    return
            else:
                await state.clear()


# **********HELP CMD**********
@main_router.message(F.text == 'Help🔫')
@main_router.message(Command("help"))          
async def help_command(message: types.Message, language: str):
    user_id = int(message.from_user.id)
    if language is None:
        try: 
            language = await get_language(user_id)
        except TypeError as e:
            logger.error(f'An error occured on {user_id}: {e}')
            await message.answer(LANGUAGES['en']['main_error'], reply_markup=keyboards.help_kb)
            return
    await message.answer(LANGUAGES[language]['help'], reply_markup=keyboards.help_kb)
   

@main_router.message(F.text == "Cancel🚩")
@main_router.message(F.text == "Скасувати🚩")
@main_router.message(F.text == "Abbrechen🚩")
async def cancel_command(message: types.Message, state: FSMContext, language: str):
    user_id = int(message.from_user.id)
    if language is None:
        try: 
            language = await get_language(user_id)
        except TypeError as e:
            logger.error(f'An error occured on {user_id}: {e}')
            await message.answer(LANGUAGES['en']['main_error'], reply_markup=keyboards.help_kb)
            return
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(LANGUAGES[language]['cancel_empty'], reply_markup=keyboards.help_kb)
    else:
        await state.clear()
        await message.answer(LANGUAGES[language]['cancel'], reply_markup=keyboards.help_kb)

# *****INFORMATION BUTTON*****
@main_router.message(F.text == "Inforamtion🗃")
@main_router.message(Command("info"))
async def info_command(message: types.Message, language: str): 
    user_id = int(message.from_user.id)
    if language is None:
        try: 
            language = await get_language(user_id)
        except TypeError as e:
            logger.error(f'An error occured on {user_id}: {e}')
            await message.answer(LANGUAGES['en']['main_error'], reply_markup=keyboards.help_kb)
            return
    await message.answer(LANGUAGES[language]['information'], reply_markup=keyboards.help_kb, parse_mode=ParseMode.HTML)

# *****CONFIG BUTTON******
@main_router.message(F.text == "Config⚙")
@main_router.message(Command("config"))                
async def config_command(message: types.Message, language: str):
    user_id = int(message.from_user.id)   
    if language is None:
        try: 
            language = await get_language(user_id)
        except TypeError as e:
            logger.error(f'An error occured on {user_id}: {e}')
            await message.answer(LANGUAGES['en']['main_error'], reply_markup=keyboards.help_kb)
            return        
    await message.answer(LANGUAGES[language]['config'], parse_mode=ParseMode.MARKDOWN, reply_markup=KEYBOARDS[language]['config'])

#Language
@main_router.message(F.text == "Language🇪🇺")
@main_router.message(F.text == "Мова🇪🇺")
@main_router.message(F.text == "Sprache🇪🇺")
async def set_language(message: types.Message, state: FSMContext, language: str):
    user_id = int(message.from_user.id)
    if language is None:
        try: 
            language = await get_language(user_id)
        except TypeError as e:
            logger.error(f'An error occured on {user_id}: {e}')
            await message.answer(LANGUAGES['en']['main_error'], reply_markup=keyboards.help_kb)
            return
    else:
        await message.answer(LANGUAGES[language]['config_language'], parse_mode=ParseMode.MARKDOWN, reply_markup=keyboards.language_keyboard)
        await state.set_state(Config.set_language)

#Ukr
@main_router.message(F.text == "Українська🇺🇦", Config.set_language)
async def ukr_language(message: types.Message, state: FSMContext, language: str):                
    user_id = int(message.from_user.id)
    cache[str(user_id)] = 'uk'
    stmt = update(User).where(User.id == user_id).values(language='uk')
    async with async_session_factory() as session:
        async with session.begin():
            try:
                await session.execute(stmt)
            except Exception as e:
                logger.error(f'An error occured on {user_id}: {e}')
                await message.answer(LANGUAGES['uk']['main_error'], reply_markup=keyboards.help_kb)
                return
            else: 
                await message.answer("Встановлена українська мова🇺🇦", reply_markup=keyboards.help_kb)
    await state.clear()

#Eng
@main_router.message(F.text == "English🇬🇧", Config.set_language)
async def ukr_language(message: types.Message, state: FSMContext):                
    user_id = int(message.from_user.id)
    cache[str(user_id)] = 'en'
    stmt = update(User).where(User.id == user_id).values(language='en')
    async with async_session_factory() as session:
        async with session.begin():
            try:
                await session.execute(stmt)
            except Exception as e:
                logger.error(f'An error occured on {user_id}: {e}')
                await message.answer(LANGUAGES['en']['main_error'], reply_markup=keyboards.help_kb)
                return
            else: 
                await message.answer("English language is set🇬🇧", reply_markup=keyboards.help_kb)
    await state.clear()   

@main_router.message(F.text == "Deutsch🇩🇪", Config.set_language)
async def ukr_language(message: types.Message, state: FSMContext):                
    user_id = int(message.from_user.id)
    cache[str(user_id)] = 'de'
    stmt = update(User).where(User.id == user_id).values(language='de')
    async with async_session_factory() as session:
        async with session.begin():
            try:
                await session.execute(stmt)
            except Exception as e:
                logger.error(f'An error occured on {user_id}: {e}')
                await message.answer(LANGUAGES['en']['main_error'], reply_markup=keyboards.help_kb)
                return
            else: 
                await message.answer("Deutsche Sprache ist eingestellt🇩🇪", reply_markup=keyboards.help_kb)
    await state.clear()                             

#Username
@main_router.message(F.text == "Username💻")
@main_router.message(F.text == "Користувач💻")
@main_router.message(F.text == "Nutzer💻")
async def set_username(message: types.Message, state: FSMContext, language: str):
    user_id = int(message.from_user.id)   
    if language is None:
        try: 
            language = await get_language(user_id)
        except TypeError as e:
            logger.error(f'An error occured on {user_id}: {e}')
            await message.answer(LANGUAGES['en']['main_error'], reply_markup=keyboards.help_kb)
            return    
    await message.answer(LANGUAGES[language]['config_username'], reply_markup=KEYBOARDS[language]['cancel'])
    await state.set_state(Config.set_username)

@main_router.message(Config.set_username)
async def new_username(message: types.Message, state: FSMContext, language: str):
    user_id = int(message.from_user.id)
    username = message.text
    if language is None:
        try: 
            language = await get_language(user_id)
        except TypeError as e:
            logger.error(f'An error occured on {user_id}: {e}')
            await message.answer(LANGUAGES['en']['main_error'], reply_markup=keyboards.help_kb)
            return
    stmt = update(User).where(User.id == user_id).values(username=username)
    async with async_session_factory() as session:
        async with session.begin():
            try:
                await session.execute(stmt)
            except exc.IntegrityError as e:
                await message.answer(LANGUAGES[language]['integrity_error'].format(username=username), parse_mode=ParseMode.MARKDOWN, reply_markup=KEYBOARDS[language]['cancel'])
                await message.answer(LANGUAGES[language]['config_username'])
                await state.set_state(Config.set_username)
            except Exception as e:
                if len(username) > 32:
                    await message.answer(LANGUAGES[language]['length_error'])
                    await message.answer(LANGUAGES[language]['config_username'])
                    await state.set_state(Config.set_username)
                else:
                    logger.error(f'An error occured on {user_id}: {e}')
                    await message.answer(LANGUAGES['en']['main_error'], reply_markup=keyboards.help_kb)
                    return
            else:
                await message.answer(LANGUAGES[language]['config_new_username'].format(username=username), parse_mode=ParseMode.MARKDOWN, reply_markup=keyboards.help_kb)
                await state.clear()


# *****TUTORIAL BUTTON*****
@main_router.message(F.text == 'Tutorial📝')
@main_router.message(Command("tutor"))
async def tutorial_button(message: types.Message, state: FSMContext, language: str):
    video_path = FSInputFile(path=LANGUAGES[language]['tutor_source'])
    user_id = int(message.from_user.id)
    if language is None:
        try: 
            language = await get_language(user_id)
        except TypeError as e:
            logger.error(f'An error occured on {user_id}: {e}')
            await message.answer(LANGUAGES['en']['main_error'], reply_markup=keyboards.help_kb)
            return
    else:
        await message.answer_video(video=video_path, caption=LANGUAGES[language]['tutor_video'], parse_mode=ParseMode.MARKDOWN)
        #await message.answer_photo(photo=photo_path, caption=LANGUAGES[language]['tutor_photo'], parse_mode=ParseMode.MARKDOWN, reply_markup=keyboards.help_kb)


# *****LEARN CMD**********
# Learn Button
@main_router.message(F.text == 'Learn📚')
@main_router.message(Command("learn"))
async def learn_button(message: types.Message, state: FSMContext, language: str):
    user_id = int(message.from_user.id)    
    if language is None:
        try: 
            language = await get_language(user_id)
        except TypeError as e:
            logger.error(f'An error occured on {user_id}: {e}')
            await message.answer(LANGUAGES['en']['main_error'], reply_markup=keyboards.help_kb)
            return
    await state.set_state(Learn.start_learn)
    await message.answer(LANGUAGES[language]['learn'], parse_mode=ParseMode.MARKDOWN)
    await message.answer(LANGUAGES[language]['learn_list'], reply_markup=KEYBOARDS[language]['cancel'])



# Create dictionary
@main_router.message(Learn.start_learn)
async def create_dictionary(message: types.Message, state: FSMContext, language: str):
    user_id = int(message.from_user.id)
    await state.update_data(valid_input=True)
    data = await state.get_data()
    if language is None:
        try: 
            language = await get_language(user_id)
        except TypeError as e:
            logger.error(f'An error occured on {user_id}: {e}')
            await message.answer(LANGUAGES['en']['main_error'], reply_markup=keyboards.help_kb)
            return
    words = message.text.split('\n')
    for line in words: 
        if len(line.split(' ')) != 2:
            data['valid_input'] = False
            await message.answer(LANGUAGES[language]['learn_error'], reply_markup=KEYBOARDS[language]['cancel'])
            await state.clear()
            await state.set_state(Learn.start_learn)
            break
    if data['valid_input'] == True:
        await message.answer(LANGUAGES[language]['completed_list'], reply_markup=keyboards.ready_button) #reply_markup=KEYBOARDS[language]['ready'])
        random.shuffle(words)
        await state.update_data(words=words, whole=len(words), missed_words=[], language=language, round=1)
        await state.set_state("test")

#webhook config
        
#HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
#WEBHOOK_HOST = f'https://testpadtgbot-acf7a4085c54.herokuapp.com'
#WEBHOOK_PATH = f'/{config.TOKEN}'
#WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

#WEBAPP_HOST = "0.0.0.0"
#WEBAPP_PORT = os.environ.get("PORT", default=8080)

# async def on_startup(bot: Bot):
#     await bot.delete_webhook(drop_pending_updates=True)
#     await bot.set_webhook(WEBHOOK_URL)
        
# async def main():    
    # dp.startup.register(on_startup)
    # app = web.Application()
    # webhook_handler = SimpleRequestHandler(
    #     dispatcher=dp,
    #     bot=bot,
    # )
    # webhook_handler.register(app, path=WEBHOOK_PATH)
    # setup_application(app, dp, bot=bot)
    # web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

#config
async def main():
    bot = Bot(token=config.TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage, events_isolation=SimpleEventIsolation())
    dp.include_router(test_router)
    dp.include_router(main_router)
    scene_registry = SceneRegistry(dp)
    scene_registry.add(TestScene)
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    asyncio.run(main())