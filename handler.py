import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

URL = 'https://api.coinranking.com/v2/coins'
API_KEY_COIN_RANKING = 'coinranking5cce4d5edc1cb646f53a01c67bd4c83636ed7f1f9146d1f5'

# ASSETS_URL = 'https://rest.coinapi.io/v1/assets'
ICONS_URL = 'https://rest.coinapi.io/v1/assets/icons/16'
API_KEY_COIN_API = '36745626-A708-48A1-A101-7586252C6832'

credentialData = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(credentialData)

db = firestore.client()


class Coin:
    def __init__(self, uuid, name, symbol, price):
        self.uuid = uuid
        self.name = name
        self.symbol = symbol
        self.price = price
        self.iconUrl = ""

    @staticmethod
    def from_json(json_dict):
        return Coin(json_dict['uuid'],
                    json_dict['name'],
                    json_dict['symbol'],
                    json_dict['price'])

    def convert_to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'symbol': self.symbol,
            'price': self.price,
            'iconUrl': self.iconUrl
        }

    def set_icon_url(self, url_string):
        self.iconUrl = url_string


def convert_coin_json_to_coin_object(coin_list, coins_json_dict_array):
    for coin in coins_json_dict_array['data']['coins']:
        coin_list.append(Coin.from_json(coin))


def set_coin_objects_icon_urls(coin_list, icons_json_dict_array):
    for coin in coin_list:
        for icon in icons_json_dict_array:
            if coin.symbol == icon['asset_id']:
                coin.set_icon_url(icon['url'])


def write_to_firebase(coin_list):
    saved_coins_count = 0
    for coin in coin_list:
        if coin.iconUrl != "":
            db.collection(u'Coins').document(coin.symbol).set(coin.convert_to_dict())
            saved_coins_count += 1
    print(saved_coins_count)


def save_crypto_data_to_firebase(event, context):
    # Request Coin Data
    headers_for_coin_api = {'X-CoinAPI-Key': API_KEY_COIN_API}
    headers_for_coin_ranking = {'x-access-token': API_KEY_COIN_RANKING}

    coins_response = requests.get(URL, headers_for_coin_ranking)
    icons_response = requests.get(ICONS_URL, headers=headers_for_coin_api)

    coins_json_dict_array = coins_response.json()
    icons_json_dict_array = icons_response.json()

    coin_list = []

    # Parse Response
    convert_coin_json_to_coin_object(coin_list, coins_json_dict_array)

    # Set Icon Urls
    set_coin_objects_icon_urls(coin_list, icons_json_dict_array)

    # Write To Firebase
    write_to_firebase(coin_list)


if __name__ == "__main__":
    save_crypto_data_to_firebase('', '')
