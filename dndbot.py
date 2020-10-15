from discord.ext import commands
import random
import json
import asyncio
import os

# https://discordapp.com/oauth2/authorize?permissions=2048&scope=bot&client_id=766162122404134942
with open("settings.json", "r") as f:
	settings = json.loads(f.read())

with open("reckless_casting.json", "r") as f:
	reckless_casting_spells = json.loads(f.read())

bot = commands.Bot(command_prefix='!')

timeout_seconds = 120
reaction_waiters = {}

print("started!")

def get_spell(spells):
	roll = random.randint(1, 8)
	if roll == 7:
		spell = "OVADRIVE"
	else:
		spell = spells[roll - 1]
	return f"{roll} {spell}"

@bot.event
async def on_reaction_add(reaction, user):
	if reaction.message.id in reaction_waiters:
		reaction_waiters[reaction.message.id].set()

@bot.command()
async def reckless(ctx, slot : int = 0):
	if slot < 0:
		await ctx.send("Negative spell slots dont exist")
		return
	if slot >= len(reckless_casting_spells):
		await ctx.send("Reckless casting doesn't have support for that high of a spell slot")
		return
	spell_list = reckless_casting_spells[slot]

	result =  get_spell(spell_list)
	result += "\n" + get_spell(spell_list)

	message = await ctx.send(result)

	watier = asyncio.Event()
	reaction_waiters[message.id] = watier

	await asyncio.wait_for(watier.wait(), timeout_seconds)

	

	await ctx.send("it happened")



if __name__ == '__main__':
	bot.run(settings.get("token"))