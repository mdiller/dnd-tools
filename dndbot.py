from discord.ext import commands
import random
import json
import os

# https://discordapp.com/oauth2/authorize?permissions=2048&scope=bot&client_id=766162122404134942
with open("reckless_casting.json", "r") as f:
	reckless_casting_spells = json.loads(f.read())

bot = commands.Bot(command_prefix='!')

print("started!")

@bot.command()
async def reckless(ctx, slot : int = 0):
	if slot < 0:
		await ctx.send("Negative spell slots dont exist")
		return
	if slot >= len(reckless_casting_spells):
		await ctx.send("Reckless casting doesn't have support for that high of a spell slot")
		return
	spell_list = reckless_casting_spells[slot]

	await ctx.send(reckless_casting_spells[3][2])

if __name__ == '__main__':
	bot.run('')