from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from aiogram.dispatcher import FSMContext

import config
import logging
from data import Data

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TG_TOKEN)


storage = MongoStorage(uri=config.MONGO_URL)
dp = Dispatcher(bot, storage=storage)

data = Data()


@dp.message_handler(commands=['start', 'cancel'], state='*')
async def start(message: types.Message, state: FSMContext):
    await state.set_state(None)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('Saņemt kultūras objektus')
    kb.add(btn)
    await message.answer('Esiet sveicināts!', reply_markup=kb)


@dp.message_handler(commands=['reload'], state='*')
async def reload(message: types.Message):
    data.reload()
    await message.answer('Dati atjaunoti')


@dp.message_handler(lambda message: message.text == 'Saņemt kultūras objektus')
async def get_objects(message: types.Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btns = []
    for category in data.objects.keys():
        btn = types.KeyboardButton(category)
        btns.append(btn)
    kb.add(*btns)
    await message.answer('Lūdzu, izvēlieties objektu:', reply_markup=kb)
    await state.set_state('show_cats')


@dp.message_handler(state='show_cats')
async def get_objects_categories(message: types.Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btns = []

    for obj in data.objects[message.text]:
        btn = types.KeyboardButton(obj)
        btns.append(btn)
    kb.add(*btns)

    await state.update_data(obj=message.text)
    await state.set_state('show_names')

    await message.answer('Lūdzu, izvēlieties objekta kategoriju:', reply_markup=kb)


@dp.message_handler(state='show_names')
async def get_objects_by_category(message: types.Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('Saņemt kultūras objektus')
    kb.add(btn)

    await message.answer('Objekti:', reply_markup=kb)

    state_data = await state.get_data()
    await state.set_state(None)
    for x in data.get_objects_by_category(state_data['obj'], message.text):
        await message.answer(x)

if __name__ == '__main__':

    executor.start_polling(dp)
