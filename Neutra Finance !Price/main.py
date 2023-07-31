import discord
import requests
import json
import pandas as pd
import mplfinance as mpf
from webserver import keep_alive
import os 
import time

client = discord.Client(intents=discord.Intents.all())
coin_id = 'neutra-finance'
url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=' + coin_id
bot_token = 'MTAzMDgwNTM5NTI3MjM2ODEzOA.GIroJg.2Hcjfp3xePRxPJmKga4zBMCPahFAIpPPc7Fj90'

def get_coin_info():
    response = requests.get(url)
    data = json.loads(response.text)
    coin_info = data[0]
    time.sleep(10)
    return coin_info

def get_chart():
    try:
        coin_info = get_coin_info()
        chart_data = requests.get('https://api.coingecko.com/api/v3/coins/' + coin_id + '/ohlc?vs_currency=usd&days=1')
        chart_data.raise_for_status()  # Raise an exception if the response is not successful
        chart_json = chart_data.json()
        ohlc = pd.DataFrame(chart_json, columns=['time', 'open', 'high', 'low', 'close'])
        ohlc['time'] = pd.to_datetime(ohlc['time'], unit='ms')
        ohlc = ohlc.set_index('time')  # Set the 'time' column as the index
        s = mpf.make_mpf_style(base_mpf_style='yahoo', rc={'axes.labelsize': 10})

        title = 'Neutra Token (NEU/USDC) - Current Price: ${:,.2f}'.format(coin_info['current_price'])
        fig, ax = mpf.plot(ohlc, type='candle', style=s, title=title, returnfig=True)
        fig.savefig('chart.png')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching chart data: {e}")


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!price'):
      coin_info = get_coin_info()
      get_chart()
      with open('chart.png', 'rb') as f:
          chart = discord.File(f)
      table = discord.Embed(title='Neutra Finance', color=0x00ff00)
      table.set_thumbnail(url=coin_info['image'])
      table.add_field(name='Current Price', value='$' + str(round(coin_info['current_price'], 2)))
      table.add_field(name='Price Change (24H)', value=str(round(coin_info['price_change_24h'], 2)) + '%')
      table.add_field(name='\n', value='\n')
      table.add_field(name='Volume (24H)', value='${:,.0f}'.format(coin_info['total_volume'])) 
      table.add_field(name='Market Cap', value='${:,.0f}'.format(coin_info['market_cap']))
      table.add_field(name='\n', value='\n')
      table.add_field(name='Neu Market', value='[Camelot Exchange](https://app.camelot.exchange/)\n[XY Finance](https://app.xy.finance/)\n[BKEX Exchange](https://www.bkex.com/en/trade/NEU_USDT)')
      table.set_footer(text='Data Provided by CoinGecko')
      await message.channel.send(embed=table)
      await message.channel.send(file=chart)

keep_alive()
TOKEN = os.environ.get("DISCORD_BOT_SECRET")
client.run(TOKEN)
