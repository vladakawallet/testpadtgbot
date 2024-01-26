from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.scene import Scene, on
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from languages import LANGUAGES
import keyboards
from keyboards import KEYBOARDS


class TestScene(Scene, state="test"): 
    @on.message.enter()
    async def on_start(self, message: Message):
        await self.wizard.update_data(attempt=0)
        data = await self.wizard.get_data()
        words = data['words'] 
        await message.answer(words[0].split(' ')[0])

    @on.callback_query(F.data == "ready")
    async def on_callback(self, callback: CallbackQuery, state: FSMContext): 
        await callback.answer("Test started!")
        await self.wizard.update_data(attempt=0)
        data = await self.wizard.get_data()
        language = data['language']
        round = data['round']
        words = data['words'] 
        await callback.message.answer(words[0].split(' ')[0], reply_markup=KEYBOARDS[language]['cancel_test'])
        await self.wizard.update_data(round=0)

    @on.message(F.text == "Exit🚩")
    @on.message(F.text == "Завершити🚩")
    @on.message(F.text == "Verlassen🚩")
    async def command_cancel(self, message: Message, state: FSMContext):
        data = await self.wizard.get_data()
        words = data['words']
        words += data['missed_words']
        language = data['language'] 
        await message.answer(LANGUAGES[language]['canceled_test'])
        await message.answer(('\n').join(words))
        await message.answer(LANGUAGES[language]['good_luck'], reply_markup=keyboards.help_kb)
        await self.wizard.clear_data()
        await self.wizard.exit()

    @on.message(F.text)
    async def on_answer(self, message: Message, state: FSMContext):
        data = await self.wizard.get_data()
        language = data['language']
        try: 
            attempt = data['attempt']
        except KeyError:
            await message.answer(LANGUAGES['en']['unknown_entry'], reply_markup=KEYBOARDS[language]['cancel_test'])
            return
        words = data['words']
        missed = data['missed_words']
        answer = message.text.lower()
        try: 
            if (answer != words[0].split(' ')[1].lower()) and (attempt < 2):
                await message.answer(LANGUAGES[language]['wrong'])
                await message.answer(words[0].split(' ')[0])
                await self.wizard.update_data(attempt=attempt+1)
            elif (answer != words[0].split(' ')[1].lower()) and (attempt == 2):
                missed_word = words.pop(0)
                missed.append(missed_word)
                await self.wizard.update_data(missed_words=missed)
                await self.wizard.update_data(words=words)
                if len(words) > 0:
                    await message.answer(LANGUAGES[language]['missed_word'].format(answer=missed_word.split(' ')[1]))
                    await self.wizard.retake()
                else: 
                    raise IndexError
            else: 
                await message.answer(LANGUAGES[language]['right'])
                words.pop(0)
                await state.update_data(words=words)
                if len(words) > 0:
                    await self.wizard.retake()
                else:
                    raise IndexError
        except IndexError:
            data = await self.wizard.get_data()
            rest = len(data['missed_words'])
            words = data['missed_words']
            whole = data['whole']
            if data['missed_words'] == []:
                await message.answer(LANGUAGES[language]['perfect_test_result'].format(result=round((100*(whole-rest))/whole, 2)),
                                     reply_markup=keyboards.help_kb, parse_mode=ParseMode.MARKDOWN)
            else:
                await message.answer(LANGUAGES[language]['test_result'].format(result=round((100*(whole-rest))/whole, 2)), parse_mode=ParseMode.MARKDOWN)
                await message.answer(('\n').join(words))
                await message.answer(LANGUAGES[language]['good_luck'], reply_markup=keyboards.help_kb)
