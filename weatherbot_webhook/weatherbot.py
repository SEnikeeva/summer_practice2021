import json
import requests
import os


"""
Обработчик запросов к telegram-bot @cloud_practice21_bot посредством webhook
"""


def send_weather(msg, geocode_request=None, weather_url=None, weather_key=None,
                 tg_url=None, tg_token=None):
    # get coords
    if msg.get('location') is not None:
        lat = msg['location']['latitude']
        lon = msg['location']['longitude']
    else:
        address = msg['text']
        geocode_resp = requests.post(url=geocode_request['url'], headers=geocode_request['headers'], json=[ address ])
        geocode_resp = json.loads(geocode_resp.text[1:-1])
        lat = geocode_resp['geo_lat']
        lon = geocode_resp['geo_lon']
    weather_resp = json.loads(requests.get(
        weather_url,
        params={
            'lat': lat,
            'lon': lon,
            'appid': weather_key,
            'units': 'metric',
            'lang': 'ru'}).text)
    # send answer
    if weather_resp.get('main') is not None:
        text = f"Температура: {weather_resp['main']['temp']}" \
               f"\nОщущается как: {weather_resp['main']['feels_like']}\n"
        for w in weather_resp['weather']:
            text += f"{w['description']}\n"
    else:
        text = 'Write address or send location'
    requests.post(
        url=tg_url.format(token=tg_token, method='sendMessage'),
        json={'chat_id': msg['chat']['id'], 'text': text,
              'reply_to_message_id': msg['message_id']}
    )


def create_geocode_req(secret, token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}",
        "X-Secret": secret
    }
    return dict(headers=headers, url="https://cleaner.dadata.ru/api/v1/clean/address")


def send_answer(msg, tg_url, tg_token, geocode_request,
                weather_url, weather_key):
    if (msg.get('text') is not None) and (msg['text'] == '/start'):
        requests.post(
            url=tg_url.format(token=tg_token, method='sendMessage'),
            json={'chat_id': msg['chat']['id'],
                  'text': 'Write address or send location'}
        )
    else:
        send_weather(msg,
                     tg_url=tg_url,
                     tg_token=tg_token,
                     geocode_request=geocode_request,
                     weather_url=weather_url,
                     weather_key=weather_key)


def handler(event, context):
    tg_token = os.environ['TG_TOKEN']
    weather_key = os.environ['WEATHER_KEY']
    geocode_key = os.environ['GEOCODE_KEY']
    geocode_token = os.environ['GEOCODE_TOKEN']

    geocode_request = create_geocode_req(geocode_key, geocode_token)
    tg_url = 'https://api.telegram.org/bot{token}/{method}'
    weather_url = 'https://api.openweathermap.org/data/2.5/weather'

    update = json.loads(event['body'], encoding='utf-8')
    message = update['message']
    send_answer(message, tg_url, tg_token, geocode_request,
                weather_url, weather_key)
