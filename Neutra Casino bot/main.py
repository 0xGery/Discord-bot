import random
from datetime import datetime, timedelta

import interactions

from webserver import keep_alive

bot = interactions.Client(token="0xGery")

balances = {}
last_claim = {}

@bot.command(
    name="roulette",
    description="Plays a game of roulette.",
    options=[
        {
            "name": "bet",
            "description": "Your bet.",
            "type": 4,  # int
            "required": True
        }
    ]
)
async def roulette(ctx: interactions.CommandContext, bet: int):
  
    if ctx.author.id not in balances or balances[ctx.author.id] < bet:
        await ctx.send("You don't have enough balance to place this bet.")
        return

    balances[ctx.author.id] -= bet
    choices = ['red', 'black', 'green']
    result = random.choice(choices)

    if result == 'green':
        await ctx.send(f'The roulette landed on {result}. You won {bet * 14}!')
        balances[ctx.author.id] += bet * 14
    else:
        await ctx.send(f'The roulette landed on {result}. You lost your bet.')

@bot.command(
    name="roll",
    description="Rolls a 6-sided dice and gamble 50 coins."
)
async def roll(ctx: interactions.CommandContext):
    if ctx.author.id not in balances or balances[ctx.author.id] < 50:
        await ctx.send("You don't have enough balance to place this bet.")
        return

    balances[ctx.author.id] -= 50
    dice = random.randint(1, 6)
    if dice > 3:
        await ctx.send(f'You rolled a {dice} and won 50 coins!')
        balances[ctx.author.id] += 100
    else:
        await ctx.send(f'You rolled a {dice} and lost your bet.')

@bot.command(
    name="daily",
    description="Gives a specific amount to users daily."
)
async def daily(ctx: interactions.CommandContext):
    now = datetime.utcnow()
    if ctx.author.id in last_claim:
        time_since_last_claim = now - last_claim[ctx.author.id]
        if time_since_last_claim < timedelta(days=1):
            await ctx.send("You can only claim your daily coins once every 24 hours.")
            return

    if ctx.author.id not in balances:
        balances[ctx.author.id] = 0

    balances[ctx.author.id] += 100
    last_claim[ctx.author.id] = now

    await ctx.send(f'You have been given 100 coins. Your balance is now {balances[ctx.author.id]}.')

@bot.command(
    name="balance",
    description="Shows the balance of the user."
)
async def balance(ctx: interactions.CommandContext):
    if ctx.author.id not in balances:
        balances[ctx.author.id] = 0
    await ctx.send(f'Your balance is {balances[ctx.author.id]}.')

keep_alive()
bot.start()
