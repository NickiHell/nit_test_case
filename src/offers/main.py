import logging

from sanic import Sanic
from sanic.request import Request
from sanic.response import json
from sanic_openapi import doc, swagger_blueprint

from offers import config
from offers import db

app = Sanic("Offer Microservice")
app.blueprint(swagger_blueprint)


@app.listener('after_server_start')
async def after_start(app, loop):
    await db.database.connect()


@app.listener('before_server_stop')
async def before_stop(app, loop):
    await db.database.disconnect()


@app.post("/offer/create/")
@doc.consumes(doc.Integer(name='user_id'))
@doc.consumes(doc.String(name='title'))
@doc.consumes(doc.String(name='text'))
async def create_offer(request: Request):
    """
    Эндпоинт для создания оффера
    """
    request = {k: request.args.get(k) for k in request.args.keys()}
    request['user_id'] = int(request['user_id'])
    query = db.offers.insert().values(**request)
    try:
        await db.database.execute(query)
    except Exception as err:
        logging.log(logging.ERROR, err)
        response = json(
            {'message': str(err)},
            status=500
        )
    else:
        response = json(
            {'message': 'OK'},
            status=200
        )
    return response


@app.post("/offer/")
@doc.consumes(doc.Integer(name='user_id'))
@doc.consumes(doc.Integer(name='offer_id'))
async def get_offer(request: Request):
    """
    Эндпоинт для получения оффера или списка оферов
    :param request: Запрос с user_id либо с offer_id
    :return: Детали оффера или список с офферами
    """
    user_id = request.args.get('user_id')
    offer_id = request.args.get('offer_id')
    query = ''
    if offer_id and user_id:
        return json(
            {'message': '???'},
            status=400
        )
    elif user_id:
        query = db.offers.select().where(
            db.offers.c.user_id == int(user_id)
        )
    elif offer_id:
        query = db.offers.select().where(
            db.offers.c.id == int(offer_id)
        )
    try:
        result = await db.database.fetch_all(query)
    except Exception as err:
        logging.log(logging.ERROR, err)
        response = json(
            {'message': str(err)},
            status=500
        )
    else:
        if result:
            result = dict(result[0]) if offer_id else dict(
                records=[dict(x) for x in result])
        response = json(
            result,
            status=200
        )

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.OFFERS_PORT)
