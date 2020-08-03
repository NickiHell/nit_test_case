import logging

import aiohttp
import jwt
from sanic import Sanic
from sanic.request import Request
from sanic.response import json
from sanic_openapi import swagger_blueprint, doc

from users import config
from users import db
from users.utils import encrypt_password, check_password

app = Sanic("User Microservice")
app.blueprint(swagger_blueprint)


@app.listener('after_server_start')
async def after_start(app, loop):
    await db.database.connect()


@app.listener('before_server_stop')
async def before_stop(app, loop):
    await db.database.disconnect()


@app.post("/user/registry/")
@doc.consumes(doc.String(name="username"))
@doc.consumes(doc.String(name='password'))
@doc.consumes(doc.String(name='email'))
async def user_registry(request: Request):
    """
    Эндпоинт для регистрации пользователя
    """
    response = json(
        {'message': 'OK'},
        status=201,
    )
    request = {k: request.args.get(k) for k in request.args.keys()}
    request['password'] = encrypt_password(request['password'])
    query = db.users.insert().values(**request)
    try:
        await db.database.execute(query)
    except Exception as err:
        logging.log(logging.ERROR, err)
        response = json(
            {'message': str(err)},
            status=500
        )
    return response


@app.post("/user/auth/")
@doc.consumes(doc.String(name='username'))
@doc.consumes(doc.String(name='password'))
async def user_auth(request: Request):
    """
    Эндпоинт для авторизации пользователя и выдачи ему JWT токена
    :param request: Запрос
    :return: Респонс с токеном или детали ошибки
    """
    response = json({}, status=401)
    request = {k: request.args.get(k) for k in request.args.keys()}
    query = db.users.select().where(
        db.users.c.username == request['username']
    )
    try:
        result = await db.database.fetch_one(query)
    except Exception as err:
        logging.log(logging.ERROR, err)
        response = json(
            {'message': str(err)},
            status=500
        )
    else:
        if result and check_password(request['password'], result['password']):
            token = jwt.encode(
                {'user_id': result['id']},
                config.SECRET_KEY,
                algorithm='HS256'
            )
            response = json(
                {
                    "access_token": token,
                    "token_type": "bearer"
                },
                reject_bytes=False
            )
    return response


@app.get("/user/{user_id}/")
@doc.consumes(doc.Integer(name="user_id"))
async def user_get(request: Request):
    """
    Ендпоинт возвращает пользователя и оферы которые с ним связаны
    :param request: Запрос
    :return: Словарь с данными пользователя и массивом со словарями,
    содержащими данные оферов
    """

    async def get_user_offers(user_id: int):
        """
        Функция фетчит офферы по id пользователя, так коммуникацию между
        микросервисами точно делать нельзя, хоть бы схему написал.
        :param user_id: id пользователя
        :return: Словарь с листом офферов
        """
        offers = []
        async with aiohttp.ClientSession() as session:
            resp = await session.post(
                f'http://{config.OFFERS_HOST}:'
                f'{config.OFFERS_PORT}/offer?user_id={user_id}'
            )
            if resp.status == 200:
                offers = await resp.json()
        return offers

    query = db.users.select().where(
        db.users.c.id == int(request.args.get('user_id'))
    )
    obj = await db.database.fetch_one(query)
    if obj:
        user_obj = dict(obj)
        user_offers = await get_user_offers(user_obj['id'])
        user_obj.update({
            'offers': user_offers['records'] if user_offers else []
        })
        result = json(user_obj)
    else:
        result = json({}, status=404)
    return result


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.USERS_PORT)
