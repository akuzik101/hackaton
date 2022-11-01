from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from aiogram.dispatcher import FSMContext

import config
import logging
import pickle

from data import Data

logging.basicConfig(level=logging.INFO)

data = Data()

storage = MongoStorage(uri=config.MONGO_URL)
bot = Bot(token=config.TG_TOKEN)

dp = Dispatcher(bot, storage=storage)


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


@dp.message_handler(lambda message: message.text in ['Saņemt kultūras objektus', 'Atpakaļ'], state='*')
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
    kb.add(types.KeyboardButton('Atpakaļ'))
    state_data = await state.get_data()

    objects: list
    i = 0
    if 'objects' not in state_data:
        objects = data.get_objects_by_category(state_data['obj'], message.text)
    else:
        objects = pickle.loads(state_data['objects'])
    print(objects)

    await message.answer('Objekti:')
    end = False
    for j in range(config.OBJ_AT_ONCE):
        try:
            await message.answer(str(objects[i]))
        except KeyError:
            end = True
            break
        i += 1
    if end:
        state_data.pop(objects)
        await state.reset_state()
        await state.reset_data()
        await message.answer('Visi rezultāti ir sniegti.', reply_markup=kb)
    else:
        kb.add(types.KeyboardButton('Parādīt vēl'))
        state_data['obj'] = pickle.dumps(objects[i:])
        await state.update_data(state_data)
        await message.answer('Izvēlieties nākamo darbību.', reply_markup=kb)


if __name__ == '__main__':
    try:
        executor.start_polling(dp)
    except KeyboardInterrupt:
        print('Shutting down...')
        dp.storage.close()
        data.c.close()
