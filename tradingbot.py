##This is just a simple sample to show how to build a bot to do arbitrary trading between huobi and gdex, do not suggest to directly use it to trade, it's suggested to optimize it before using for security and efficiency reasons.
## Libraries https://github.com/HuobiRDCenter/huobi_Python and https://github.com/bitshares/python-bitshares are used to connect huobi and BTS.


## Key of huobi account
APIKEY='**********************************'
SECERTKEY='*******************************'

import time

from bitshares import BitShares
from bitshares.account import Account
from bitshares.market import Market

from huobi_Python.huobi.client.generic import GenericClient
from huobi_Python.huobi.client.market import MarketClient
from huobi_Python.huobi.client.account import AccountClient
from huobi_Python.huobi.client.trade import TradeClient
from huobi_Python.huobi.constant.definition import DepthStep

## create huobi clients
generic_client = GenericClient()
market_client = MarketClient()

account_client = AccountClient(api_key=APIKEY, secret_key=SECERTKEY)
trade_client = TradeClient(api_key=APIKEY, secret_key=SECERTKEY)

##create bts clients
bts = BitShares("wss://ws.gdex.top")
pw = input("please input the pw: ")
bts.wallet.unlock(pw)
dexmarket = Market('BTS/GDEX.USDT', blockchain_instance=bts)

while True:
    ##get huobi and bts tickers
    huobidepth = market_client.get_pricedepth("btsusdt", DepthStep.STEP0, 1)
    dexticker = dexmarket.orderbook(limit=1)

    dexbid = dexticker['bids'][0]
    dexask = dexticker['asks'][0]

    huobibid = huobidepth.bids[0]
    huobiask = huobidepth.asks[0]
    
    ##compare the ticker and place orders if there are trading chances:
    if dexbid.price > huobiask.price * 1.006 and min(dexbid['quote'].amount, huobiask.amount) > 100:
        huobibuyorder_id = trade_client.create_order(symbol='btsusdt', account_id=88888888, order_type='buy-limit',
                                         source="api", amount=100, price=huobiask.price)
        dexmarket.sell(price=dexbid.price, amount=100, account='test')
    else:
        print('no chance for trading, dex bid price is %.5f and huobi ask price is %.5f' % (dexbid.price, huobiask.price))

    if dexask.price*1.006 < huobibid.price and min(dexask['quote'].amount,huobiask.amount)>100:
        huobisellorder_id = trade_client.create_order(symbol='btsusdt', account_id=88888888, order_type='sell-limit',
                                                     source="api", amount=100, price=huobibid.price)
        dexmarket.buy(price=dexask.price, amount=100, account='test')
    else:
        print('no chance for trading, dex ask price is %.5f and huobi bid price is %.5f' % (dexask.price, huobibid.price))
    time.sleep(5)
