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

reaction_emoji = ["{}\N{COMBINING ENCLOSING KEYCAP}".format(num) for num in range(1, 9)]

print("started!")

def get_spell(spells, roll, is_multicast=False):
	if roll == 8:
		spell = "FIZZLE 😢" if is_multicast else "MULTICAST!"
	else:
		spell = spells[roll - 1]
	return spell

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

	rolls = [ random.randint(1, 8), random.randint(1, 8) ]

	if slot == 0: # only roll once for cantrips table
		rolls = [ rolls[0] ]

	result = ""
	for roll in rolls:
		result += f"{roll} {get_spell(spell_list, roll)}\n"

	message = await ctx.send(result)
	# emojis = [ reaction_emoji[rolls[0] - 1], reaction_emoji[rolls[1] - 1] ]

	if 8 not in rolls:
		return
	
	multicast_emoji = bot.get_emoji(settings.get("multicast_emoji"))
	emojis = [ multicast_emoji ]
	for emoji in emojis:
		await message.add_reaction(emoji)

	waiter = asyncio.Event()
	reaction_waiters[message.id] = waiter

	clicked_emoji = None
	try:
		while clicked_emoji is None:
			await asyncio.wait_for(waiter.wait(), timeout_seconds)
			message = await ctx.fetch_message(message.id)
			for reaction in message.reactions:
				if reaction.emoji not in emojis:
					continue
				users = await reaction.users().flatten()
				if ctx.message.author in users:
					clicked_emoji = reaction.emoji
			waiter.clear()
	except asyncio.TimeoutError:
		clicked_emoji = None
	finally:
		del reaction_waiters[message.id]

	for emoji in emojis:
		await message.remove_reaction(emoji, bot.user)


	if clicked_emoji:
		# for now, this only triggers if its a multicast
		rolls = [ random.randint(1, 8), random.randint(1, 8) ]
		lines = []
		lines.append("__Multicast:__")
		for i in range(len(rolls)):
			line = f"{rolls[i]} {get_spell(spell_list, rolls[i], True)}"
			if rolls[i] != 8 and 8 in rolls:
				line = f"~~{line}~~"
			lines.append(line)
		result += "\n" + "\n".join(lines)
		await message.edit(content=result)

		# selected_roll = reaction_emoji.index(clicked_emoji) + 1
		# await ctx.send(f"!spell {get_spell(spell_list, selected_roll)}")
	else:
		print("thing not clicked")



if __name__ == '__main__':
	bot.run(settings.get("token"))


# todo implement only roll once for casting a cantrip
# todo handle timeout errors