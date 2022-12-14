from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from aiogram.dispatcher import FSMContext

from geopy.geocoders import Nominatim

import logging
import pickle
import asyncio
import base64

from data import Data
import config

logging.basicConfig(level=logging.INFO)

geolocator = Nominatim(user_agent='kulturas_kompass')

data = Data()
loop = asyncio.new_event_loop()
loop.run_until_complete(data.init())

storage = MongoStorage(uri=config.MONGO_URL)
bot = Bot(token=config.TG_TOKEN)

dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start', 'cancel'], state='*')
async def start(message: types.Message, state: FSMContext):
    await state.set_state(None)
    await state.reset_data()
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton('Sūtīt pašreizējo ģeopozīciju', request_location=True)
    kb.add(btn)
    kb.add(types.KeyboardButton('Sūtīt adresi'))
    await message.answer('Esiet sveicināts!', reply_markup=kb)


@dp.message_handler(commands=['ping'], state='*')
async def ping(message: types.Message):
    await message.answer('PONG!')


@dp.message_handler(commands=['reload'], state='*')
async def reload(message: types.Message):
    await data.reload()
    await message.answer('Dati atjaunoti')

@dp.message_handler(commands=['loc', 'location'], state='*')
@dp.message_handler(lambda message: message.text == 'Sūtīt adresi', state='*')
async def set_location_by_address(message: types.Message, state: FSMContext):
    await state.update_data(state_bak=await state.get_state())
    await state.set_state('loc')
    await message.answer('Lūdzu, ievadiet adresi')

@dp.message_handler(content_types=['text'], state='loc')
async def process_location_by_address(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    await state.set_state(state_data['state_bak'])
    await state.update_data(state_bak=None)
    location = geolocator.geocode(message.text)
    await state.update_data(loc=(location.latitude, location.longitude))
    await message.answer('Saņemta šāda ģeopozīcija:')
    await bot.send_location(chat_id=message.from_id, latitude=location.latitude, longitude=location.longitude)
    kb = None
    if not await state.get_state():
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton('Saņemt kultūras objektus'))
    await message.answer(location.address, reply_markup=kb)
    

@dp.message_handler(content_types=['location'], state='*')
async def get_location(message: types.Message, state: FSMContext):
    await state.update_data(loc=(message.location.latitude, message.location.longitude))
    if await state.get_state() not in ['show_obj', 'show_cats']:
        await state.set_state('show_obj')
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton('Saņemt kultūras objektus'))
    await message.answer('Ģeopozīcija ir saņemta', reply_markup=kb)


@dp.message_handler(lambda message: message.text in ['Saņemt kultūras objektus', 'Atpakaļ'], state='*')
async def get_objects(message: types.Message, state: FSMContext):
    await state.update_data(objects=None)
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
    btns = [types.KeyboardButton('Atpakaļ')]

    for obj in data.objects[message.text]:
        btn = types.KeyboardButton(obj)
        btns.append(btn)
    for btn in btns:
        kb.row(btn)

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
    if 'objects' not in state_data or state_data['objects'] is None:
        objects = data.get_objects_by_category(state_data['obj'], message.text)
        for obj in objects:
            obj.set_distance_to(state_data['loc'])
        objects.sort(key=lambda obj: obj.data['distance'])
    else:
        objects = pickle.loads(base64.standard_b64decode(state_data['objects']))

    await message.answer('Objekti:')
    end = False
    for j in range(config.OBJ_AT_ONCE):
        try:
            if objects[i].data['image_url'].value:
                try:
                    await bot.send_photo(photo=objects[i].data['image_url'].value, chat_id=message.from_id)
                except:
                    pass
            await message.answer(str(objects[i]))
        except IndexError:
            end = True
            break
        i += 1
    if end:
        await state.set_state(None)
        await state.update_data(objects=None)
        await message.answer('Visi rezultāti ir sniegti.', reply_markup=kb)
    else:
        kb.add(types.KeyboardButton('Ielādēt vēl'))
        serialized_objects = base64.standard_b64encode(pickle.dumps(objects[i:]))
        await state.update_data(objects=serialized_objects)
        await message.answer('Izvēlieties nākamo darbību.', reply_markup=kb)


if __name__ == '__main__':
    try:
        executor.start_polling(dp)
    finally:
        print('Shutting down...')
        loop.run_until_complete(dp.storage.close())
        data.c.close()
        data.db.close()
