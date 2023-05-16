import discord # pip install py-cord
import json
import random as rnd
import os
import time
from datetime import datetime

boot_time = int(time.time())

bot = discord.Bot()

token_file = open('token.json')
token_file_data = json.load(token_file)
ownerid = token_file_data["owner_id"]
token = token_file_data["token"]
token_file.close()

details_string = {}
last_drill_message = {}
last_drill_time = {}

def d6():
	return rnd.randint(1,6)

def list_of_d6(count):
	out = []
	for i in range(count):
		out.append(d6())
	return out

def tracelog(s, channel):
	print(s)
	details_string[channel] += s + "\n"

def yn(bool):
	return "Yes" if bool else "No"

@bot.event
async def on_ready():
	boot_time = int(time.time())
	print(f"{bot.user} is ready and online!")

@bot.command(description="Shuts down the bot. Will not work unless you own the bot.")
async def kill(ctx):
	if ctx.author.id == ownerid:
		print(f"Recieved valid kill request ({ctx.author.id})")
		await ctx.respond(f"Shutting down.")
		print("Shutting down...")
		await bot.close()
	else:
		print(f"Refused invalud kill request ({ctx.author.id})")
		await ctx.respond(f"Only <@{ownerid}> may use this command.",ephemeral=True)
		

@bot.command(description="Traces all dice rolls for the last Combat Drill roll in this channel")
async def trace(ctx):
	channel_id = ctx.channel.id
	if channel_id in details_string:
		msg = f"Trace for Combat Drill roll performed <t:{last_drill_time[channel_id]}:R>: {last_drill_message[channel_id]}\n```v\n{details_string[channel_id]}```"
		if len(msg) > 2000:
			with open("message.txt","w") as file:
				file.write(details_string[channel_id])
			await ctx.respond(f"Trace for Combat Drill roll performed <t:{last_drill_time[channel_id]}:R>: {last_drill_message[channel_id]}\nThe message is too long to send. Please view the attached file.",file=discord.File('message.txt'))
			os.remove('message.txt')
			print(f"Sent trace with length {len(details_string[channel_id])} as file")
		else:
			await ctx.respond(msg)
			print(f"Sent trace with length {len(msg)}")
	else:
		await ctx.respond(f"No Combat Drill rolls recorded in this channel since <t:{boot_time}:R>.",ephemeral=True)

@bot.command(description="Roll damage for Combat Drill")
async def combat_drill(ctx, 
	target_has_status: discord.Option(bool, "Mark TRUE if the target of the attack is Prone, Immobilized, or Stunned."), 
	crit: discord.Option(bool, "Mark TRUE if the roll to attack was a critical hit."), 
	bonus_dice: discord.Option(int, "The amount of bonus dice applied to the attack roll *before* rolling.", required=False, default=0), 
	bonus_flat: discord.Option(int,"Flat bonus damage applied to the attack roll *before* rolling.",required=False, default=0)):
	if bonus_dice > 10:
		await ctx.respond("☢️ Please roll at most 10 bonus dice.",ephemeral=True)
		print(f"Refused roll request with {bonus_dice} bonus dice")
		return
	channel_id = ctx.channel.id
	details_string[channel_id] = ""
	
	kinetic = list_of_d6(6 if crit else 3)
	energy = list_of_d6(2 if crit else 1)
	bonus = list_of_d6(bonus_dice * (2 if crit else 1))
	
	tracelog("--- Initial dice results ---", channel_id)
	tracelog(f"Kinetic: {kinetic}", channel_id)
	tracelog(f"Energy: {energy}", channel_id)
	tracelog(f"Bonus: {bonus}", channel_id)
	
	heat = 0
	
	while 1 in kinetic:
		tracelog("--- Kinetic reroll loop ---", channel_id)
		for i in range(len(kinetic)):
			if kinetic[i] == 1:
				tracelog(f"Rerolled result in position {i} (+1 heat)", channel_id)
				kinetic[i] = d6()
				heat += 1
				if target_has_status:
					tracelog(f"Added bonus d6", channel_id)
					bonus.append(d6())
					if crit:
						tracelog(f"Added bonus d6", channel_id)
						bonus.append(d6())
		tracelog(f"Reroll pass results: {kinetic}", channel_id)
	
	tracelog("--- END OF KINETIC DAMAGE ---", channel_id)
	tracelog(f"Final results: {kinetic}", channel_id)
	tracelog(f"Current Bonus dice: {bonus}", channel_id)
	
	while 1 in energy:
		tracelog("--- Energy reroll loop ---", channel_id)
		for i in range(len(energy)):
			if energy[i] == 1:
				tracelog(f"Rerolled result in position {i} (+1 heat)", channel_id)
				energy[i] = d6()
				heat += 1
				if target_has_status:
					tracelog(f"Added bonus d6", channel_id)
					bonus.append(d6())
					if crit:
						tracelog(f"Added bonus d6", channel_id)
						bonus.append(d6())
		tracelog(f"Reroll pass results: {energy}", channel_id)

	tracelog("--- END OF ENERGY DAMAGE ---", channel_id)
	tracelog(f"Final results: {energy}", channel_id)
	tracelog(f"Current Bonus dice: {bonus}", channel_id)
	
	while 1 in bonus:
		tracelog("--- Bonus reroll loop ---", channel_id)
		for i in range(len(bonus)):
			if bonus[i] == 1:
				tracelog(f"Rerolled result in position {i} (+1 heat)", channel_id)
				bonus[i] = d6()
				heat += 1
				if target_has_status:
					tracelog(f"Added bonus d6", channel_id)
					bonus.append(d6())
					if crit:
						tracelog(f"Added bonus d6", channel_id)
						bonus.append(d6())
		tracelog(f"Reroll pass results: {bonus}", channel_id)
	
	tracelog("--- END OF BONUS DAMAGE ---", channel_id)
	tracelog(f"Final results: {bonus}", channel_id)
	
	kinetic.sort()
	energy.sort()
	bonus.sort()
	
	tracelog("--- Sorting ---", channel_id)
	tracelog(f"Kinetic: {kinetic}", channel_id)
	tracelog(f"Energy: {energy}", channel_id)
	tracelog(f"Bonus: {bonus}", channel_id)
	
	if crit:
		lower_bound_kinetic = int(len(kinetic)/2)
		lower_bound_energy = int(len(energy)/2)
		lower_bound_bonus = int(len(bonus)/2)
		
		kinetic = kinetic[lower_bound_kinetic:]
		energy = energy[lower_bound_energy:]
		bonus = bonus[lower_bound_bonus:]
		
		tracelog("--- After crit split ---", channel_id)
		tracelog(f"Kinetic: {kinetic}", channel_id)
		tracelog(f"Energy: {energy}", channel_id)
		tracelog(f"Bonus: {bonus}", channel_id)
	
	kinetic_total = sum(kinetic)
	energy_total = sum(energy)
	bonus_total = sum(bonus)+bonus_flat
	
	full_total = kinetic_total + energy_total + bonus_total
	
	tracelog("--- Totals ---", channel_id)
	tracelog(f"Kinetic damage: {kinetic_total}", channel_id)
	tracelog(f"Energy damage: {energy_total}", channel_id)
	tracelog(f"Bonus damage: {bonus_total}", channel_id)
	tracelog(f"Heat generated: {heat}", channel_id)
	tracelog(f"Full damage: {full_total}", channel_id)
	
	#message = f"**__Combat Drill__**\n🎯 Crit: **{yn(crit)}**\n💫 Status Effect: **{yn(target_has_status)}**\n{f'🎲 Initial Bonus: **{bonus_dice}d6 + {bonus_flat}**' if bonus_dice > 0 or bonus_flat > 0 else ''}\n\n⚔️ Kinetic: **{str(kinetic_total)}** `{str(kinetic)}`\n⚡ Energy: **{str(energy_total)}** `{str(energy)}`\n🎲 Bonus: **{str(bonus_total)}** `{str(bonus)}`\n🔥 Heat taken: **{str(heat)}**\n\n**Total damage: {str(full_total)}**"
	
	message = "**__Combat Drill__**"
	message += f"\n🎯 Crit: **{yn(crit)}**"
	message += f"\n💫 Status Effect: **{yn(target_has_status)}**"
	
	if bonus_dice > 0 and bonus_flat > 0:
		message += f"\n🎲 Initial Bonus: **{bonus_dice}d6 + {bonus_flat}**"
	elif bonus_dice > 0:
		message += f"\n🎲 Initial Bonus: **{bonus_dice}d6**"
	elif bonus_flat > 0:
		message += f"\n🎲 Initial Bonus: **{bonus_flat}** (flat)"
	
	message += f"\n\n⚔️ Kinetic: **{str(kinetic_total)}** `{str(kinetic)}`\n⚡ Energy: **{str(energy_total)}** `{str(energy)}`\n🎲 Bonus: **{str(bonus_total)}** `{str(bonus)}`\n🔥 Heat taken: **{str(heat)}**\n\n**Total damage: {str(full_total)}**"
	
	sent_message = await ctx.respond(message)
	sent_message = await sent_message.original_response()
	
	time_string = sent_message.created_at
	dt = datetime.fromisoformat(str(time_string))
	epoch = dt.timestamp()
	last_drill_time[channel_id] = round(epoch)
	last_drill_message[channel_id] = sent_message.jump_url

bot.run(token)