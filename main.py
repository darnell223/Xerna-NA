import discord
import time
import os
import random
import sqlite3
import requests
import math
import json
import elogain

from replit import db
from discord.utils import get
from discord.ext import commands, tasks
from PIL import Image, ImageFont, ImageDraw
from threading import Timer

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.reactions = True

client = commands.Bot(command_prefix="=", intents=intents)

client.remove_command('help')

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))
	await client.change_presence(status=discord.Status.idle,
								 activity=discord.Activity(
									 type=discord.ActivityType.watching,
									 name=f"over B4"))


@client.event
async def on_raw_reaction_add(payload):
	channel_id = payload.channel_id
	message_id = payload.message_id
	with open('./databases/voidids.json', 'r') as file:
		voididsdata = json.load(file)

		if str(message_id) in voididsdata.__str__():
			channel = client.get_channel(channel_id)

			game = channel.name
			game = game.replace('-', '')
			gameid = game.replace("game", "")
			with open('./databases/gamelogs.json', 'r') as file:
				gamelogsdata = json.load(file)

			if gamelogsdata[gameid]['voids'] + 1 >= 5:
				gamelogsdata[gameid]['voids'] += 1
				gamelogsdata[gameid]['winner'] = 'void'

				with open('./databases/gamelogs.json', 'w') as updategamelogs:
					json.dump(gamelogsdata, updategamelogs, indent=4)

				await channel.send(
					f"Succesfully voided game#`{gameid}`! Closing channels in 15 seconds!"
				)

				gameschannel = channel.guild.get_channel(949106669823066162)

				embed = discord.Embed()
				embed.add_field(name="GAME ID: {}".format(gameid),
								value="status: voided",
								inline=False)
				await gameschannel.send(embed=embed)

				time.sleep(15)

				num1 = channel.name
				num2 = num1.replace('-', '#')
				num3 = num2.replace('g', 'G')
				num4 = num3 + " | Team "

				callchannel1name = num4 + '1'
				callchannel2name = num4 + '2'

				callchannel1 = discord.utils.get(channel.guild.channels,
												 name=callchannel1name)
				callchannel2 = discord.utils.get(channel.guild.channels,
												 name=callchannel2name)

				await callchannel1.delete()
				await callchannel2.delete()
				await channel.delete()

			else:
				gamelogsdata[gameid]['voids'] += 1

				with open('./databases/gamelogs.json', 'w') as updategamelogs:
					json.dump(gamelogsdata, updategamelogs, indent=4)


@client.event
async def on_raw_reaction_remove(payload):
	channel_id = payload.channel_id
	message_id = payload.message_id
	with open('./databases/voidids.json', 'r') as file:
		voididsdata = json.load(file)

		if str(message_id) in voididsdata.__str__():
			reactionchannel = client.get_channel(channel_id)

			game = reactionchannel.name
			game = game.replace('-', '')
			gameid = game.replace("game", "")

			with open('./databases/gamelogs.json', 'r') as file:
				gamelogsdata = json.load(file)

				gamelogsdata[gameid]['voids'] -= 1

				with open('./databases/gamelogs.json', 'w') as updategamelogs:
					json.dump(gamelogsdata, updategamelogs, indent=4)


@client.event
async def on_voice_state_update(member, before, after):
	member_id = str(member.id)
	channelid = ""

	member_id = str(member.id)

	try:
		with open('./databases/queuestats.json', 'r') as file:
			voice_member_data = json.load(file)
			new_voice_member_channel = str(member.voice.channel.id)
			new_voice_member_id = str(member.id)
			members = ""
			voice_member_data[new_voice_member_channel] = []

			if new_voice_member_channel != "949055260914229308":
				return

			for user in member.voice.channel.members:
				voice_member_data[new_voice_member_channel] += [user.id]
			# Update existing voice data
			if new_voice_member_channel in voice_member_data:
				with open('./databases/queuestats.json',
						  'w') as update_voice_member_data:
					json.dump(voice_member_data,
							  update_voice_member_data,
							  indent=4)

					time.sleep(1)

			# Add new voice data
			else:
				voice_member_data[new_voice_member_channel] = [
					new_voice_member_id
				]
				with open('./databases/queuestats.json',
						  'w') as new_voice_member_data:
					json.dump(voice_member_data,
							  new_voice_member_data,
							  indent=4)

					time.sleep(1)

	except AttributeError:
		# Remove voice data
		for remove_keys, remove_values in voice_member_data.items():
			if member_id in remove_values:
				remove_values.remove(member_id)

	else:
		database = open('./databases/queuestats.json', 'r')
		maxdata = open('./databases/max.json', 'r')
		voice_member_data = json.load(database)
		maxdata = json.load(maxdata)

		members = 0
		for users in voice_member_data['949055260914229308']:
			members += 1

		if members == maxdata['max']:
			server = member.guild

			db['game'] += 1
			gameid = db['game']

			totalamt = int(maxdata['max'])

			category = discord.utils.get(server.channels,
										 id=949055260914229308)

			gamecall = await server.create_voice_channel(
				f'Game#{gameid} | Team Pick', category=category)
			gamecall1 = await server.create_voice_channel(
				f'Game#{gameid} | Team 1', category=category)
			gamecall2 = await server.create_voice_channel(
				f'Game#{gameid} | Team 2', category=category)
			gamechannel = await server.create_text_channel(f'Game {gameid}',
														   category=category)

			await gamecall.set_permissions(server.default_role, connect=False)
			await gamecall1.set_permissions(server.default_role, connect=False)
			await gamecall2.set_permissions(server.default_role, connect=False)
			await gamechannel.set_permissions(server.default_role,
											  view_channel=False)

			player = 1

			with open('./databases/gamelogs.json', 'r') as file:
				gamelogsdata = json.load(file)
				gamelogsdata[gameid] = {}
				gamelogsdata[gameid]['allplayers'] = []
				gamelogsdata[gameid]['captains'] = []
				gamelogsdata[gameid]['picked'] = []
				gamelogsdata[gameid]['team1'] = []
				gamelogsdata[gameid]['team2'] = []

				gamelogsdata[gameid]['scored'] = False
				gamelogsdata[gameid]['proof'] = False
				gamelogsdata[gameid]['picksdone'] = False
				gamelogsdata[gameid]['pick'] = 1
				gamelogsdata[gameid]['winner'] = 'none'
				gamelogsdata[gameid]['voids'] = 0
				gamelogsdata[gameid]['voidid'] = ''

				captains = 1
				team = 1

				embed = discord.Embed()
				teamoneplayers = ""
				teamtwoplayers = ""
				remainingplayers = ""

				for userid in voice_member_data['949055260914229308']:
					captain = False
					if captains < 3:
						gamelogsdata[gameid]['captains'] += [userid]
						if team == 1:
							gamelogsdata[gameid]['team1'] += [userid]
							team += 1
							teamoneplayers += f"CAPTAIN: <@{userid}>\n"
						elif team == 2:
							gamelogsdata[gameid]['team2'] += [userid]
							teamtwoplayers += f"CAPTAIN: <@{userid}>\n"
						captains += 1

						captain = True

					if captain != True:
						remainingplayers += f"<@{userid}>"
					gamelogsdata[gameid]['allplayers'] += [userid]
					userid = int(userid)
					member = server.get_member(userid)

					await gamecall.set_permissions(member, connect=True)
					await gamechannel.set_permissions(member,
													  view_channel=True)

					await member.move_to(gamecall)

				embed.add_field(name="TEAM ONE\n===========",
								value=teamoneplayers,
								inline=False)
				embed.add_field(name="TEAM TWO\n===========",
								value=teamtwoplayers,
								inline=False)
				embed.add_field(name="REMAINING\n===========",
								value=remainingplayers,
								inline=False)

				await gamechannel.send(embed=embed)

				with open('./databases/gamelogs.json', 'w') as updategamelogs:
					json.dump(gamelogsdata, updategamelogs, indent=4)


@client.command()
async def register(ctx, username=None):
	if str(ctx.channel.id) != "949132916720558141":
		await ctx.message.delete()
		return

	if username == None:
		await ctx.send("Please provide a username!")
		return

	with open('./databases/playerstats.json', 'r') as file:
		playersdata = json.load(file)
		try:
			check = playersdata[str(ctx.author.id)]['username']
		except:
			playersdata[ctx.author.id] = {}
			playersdata[ctx.author.id]['username'] = username
			playersdata[ctx.author.id]['elo'] = 0
			playersdata[ctx.author.id]['wins'] = 0
			playersdata[ctx.author.id]['losses'] = 0
			with open('./databases/playerstats.json',
					  'w') as updateplayerstats:
				json.dump(playersdata, updateplayerstats, indent=4)

		
			
			await ctx.send(f"Successfully registered as `{username}`!")

		else:
			playersdata[str(ctx.author.id)]['username'] = username
			with open('./databases/playerstats.json',
					  'w') as updateplayerstats:
				json.dump(playersdata, updateplayerstats, indent=4)
			await ctx.send(f"Re-registered as `{username}`!")

		member = ctx.guild.get_member(ctx.author.id)
		role = get(ctx.guild.roles, name="[ Scrimmers ]")
		await member.add_roles(role)

		authorid = str(ctx.author.id)

		with open('./databases/playerstats.json', 'r') as file:
			playersdata = json.load(file)

			nick = f"[{playersdata[authorid]['elo']}] {playersdata[authorid]['username']}"

			try:
				await member.edit(nick=nick)
			except:
				pass


@client.command()
@commands.has_permissions(administrator=True)
async def setMaxQueue(ctx, max=None):
	if max == None:
		await ctx.send('You did not provide a number!')
		return
	try:
		int(max)
	except:
		await ctx.send(
			f'The number you provided (`{max}`) is not a valid number!')
		return

	with open('./databases/max.json', 'r') as file:
		voice_member_data = json.load(file)
		change = 'max'
		queueCap = int(max)

		voice_member_data[change] = queueCap
		with open('./databases/max.json', 'w') as new_voice_member_data:
			json.dump(voice_member_data, new_voice_member_data, indent=4)

			time.sleep(1)

		await ctx.send(f"Set queue limit to `{queueCap}`!")


@client.command()
async def score(ctx):
	game = ctx.channel.name
	game = game.replace('-', '')
	gameid = game.replace("game", "")

	attachment = ctx.message.attachments[0]
	file = ''

	if str(ctx.channel.category.id) != "949055945005228052":
		await ctx.send('This is not a game channel!')
		return

	try:
		image_types = ["png", "jpeg", "gif", "jpg"]

		if any(attachment.filename.lower().endswith(image)
			   for image in image_types):
			with open('./databases/gamelogs.json', 'r') as file:
				gamelogsdata = json.load(file)
				if gamelogsdata[gameid]['proof'] == True:
					await ctx.send(
						f'There is already submited proof for game#`{gameid}`!'
					)
					return
				else:
					file = await attachment.save(f"{game}.png")
					gamelogsdata[gameid]['proof'] = True
					with open('./databases/gamelogs.json',
							  'w') as updategamelogsdata:
						json.dump(gamelogsdata, updategamelogsdata, indent=4)
		else:
			await ctx.send("Please provide an image to score!")
			return

	except IndexError:
		await ctx.send('You did not provide an attachment image!')

	else:
		scoringchannel = ctx.guild.get_channel(949106161532166154)

		teamone = ""
		teamtwo = ""

		for userid in gamelogsdata[gameid][f'team1']:
			with open('./databases/playerstats.json', 'r') as file:
				teamone += f"<@{str(userid)}>\n"

		for userid in gamelogsdata[gameid][f'team2']:
			with open('./databases/playerstats.json', 'r') as file:
				teamtwo += f"<@{str(userid)}>\n"

		await scoringchannel.send(
			f"{game} results! (Please delete this game's data when scored!)")
		await scoringchannel.send(file=discord.File(f"{game}.png"))

		await scoringchannel.send(
			f"TEAM ONE\n===========\n{teamone}\n\nTEAM TWO\n===========\n{teamtwo}"
		)

		os.remove(f"{game}.png")

		await ctx.send(
			f"`Game#{gameid}` has been scored! Closing channels in 15 seconds!"
		)

		start = time.time()
		while time.time() < start + 15:
			pass

		textchannel = ctx.channel
		num1 = textchannel.name
		num2 = num1.replace('-', '#')
		num3 = num2.replace('g', 'G')
		num4 = num3 + " | Team "

		callchannel1name = num4 + '1'
		callchannel2name = num4 + '2'

		callchannel1 = discord.utils.get(ctx.guild.channels,
										 name=callchannel1name)
		callchannel2 = discord.utils.get(ctx.guild.channels,
										 name=callchannel2name)

		await callchannel1.delete()
		await callchannel2.delete()
		await textchannel.delete()


@client.command()
@commands.has_role('Scorers')
async def submit(ctx, game=None, winner=None):
	with open('./databases/gamelogs.json', 'r') as file:
		gamelogsdata = json.load(file)

	try:
		int(game)
	except:
		await ctx.send(f"`{game}` is not a valid number!")
		return

	try:
		int(winner)
	except:
		if winner == "void":
			winner = "voided"
		else:
			await ctx.send(
				f"`{winner}` is not a valid winner! Please do `1` for team 1, `2` for team 2, or `'void'` to void!"
			)
			return

	loser = 0

	if winner == '1':
		loser = 2

	elif winner == '2':
		loser = 1

	try:
		if gamelogsdata[game]['scored'] == True:
			await ctx.send(f"Game #`{game}` has already been scored!")
		else:
			gamelogsdata[game]['scored'] = True
			gamelogsdata[game]['winner'] = winner
			with open('./databases/gamelogs.json', 'w') as updategamelogsdata:
				json.dump(gamelogsdata, updategamelogsdata, indent=4)

			winningteam = ""
			losingteam = ""

			if winner == "voided":
				await ctx.send(f"Succesfully voided game#`{game}`!")

				gameschannel = ctx.guild.get_channel(949106669823066162)

				embed = discord.Embed()
				embed.add_field(name="GAME ID: {}".format(game),
								value="status: voided",
								inline=False)
				await gameschannel.send(embed=embed)

			else:
				for userid in gamelogsdata[game][f'team{winner}']:
					with open('./databases/playerstats.json', 'r') as file:
						playerstatsdata = json.load(file)
						beforeelo = playerstatsdata[str(userid)]['elo']
						elogained = elogain.getaddelo(beforeelo)
						playerstatsdata[str(userid)]['elo'] += elogained
						with open('./databases/playerstats.json',
								  'w') as updatestatsdata:
							json.dump(playerstatsdata,
									  updatestatsdata,
									  indent=4)

						server = ctx.guild
						member = server.get_member(userid)
						authorid = str(userid)
						with open('./databases/playerstats.json', 'r') as file:
							playersdata = json.load(file)
							nick = f"[{playersdata[authorid]['elo']}] {playersdata[authorid]['username']}"

							winningteam += f"<@{str(userid)}> - `{beforeelo}` >> `{beforeelo + elogained}`\n"

							try:
								await member.edit(nick=nick)
							except:
								pass

				for userid in gamelogsdata[game][f'team{loser}']:
					with open('./databases/playerstats.json', 'r') as file:
						playerstatsdata = json.load(file)
						beforeelo = playerstatsdata[str(userid)]['elo']
						elolost = elogain.getloseelo(beforeelo)
						if playerstatsdata[str(userid)]['elo'] - elolost <= 0:
							playerstatsdata[str(userid)]['elo'] = 0
						else:
							playerstatsdata[str(userid)]['elo'] -= elolost
						with open('./databases/playerstats.json',
								  'w') as updatestatsdata:
							json.dump(playerstatsdata,
									  updatestatsdata,
									  indent=4)

						server = ctx.guild
						member = server.get_member(userid)
						authorid = str(userid)
						with open('./databases/playerstats.json', 'r') as file:
							playersdata = json.load(file)
							nick = f"[{playersdata[authorid]['elo']}] {playersdata[authorid]['username']}"
							afterelo = beforeelo - elolost
							if afterelo < 0:
								afterelo = 0

							losingteam += f"<@{str(userid)}> - `{beforeelo}` >> `{afterelo}`\n"

							try:
								await member.edit(nick=nick)
							except:
								pass

				embed = discord.Embed()
				embed.add_field(name="GAME ID: {}".format(game),
								value="status: finished",
								inline=False)
				embed.add_field(name="WINNING TEAM\n===========".format(game),
								value=winningteam,
								inline=False)
				embed.add_field(name="LOSING TEAM\n===========".format(game),
								value=losingteam,
								inline=False)

				gameschannel = ctx.guild.get_channel(949106669823066162)

				await ctx.send(f"Succesfully scored game#`{game}`!")
				await gameschannel.send(embed=embed)

	except KeyError as e:
		print(e)
		await ctx.send(f"There is no game with the ID: `{game}`!")


@client.command()
async def void(ctx):
	if str(ctx.channel.category.id) != "949055945005228052":
		await ctx.send('This is not a game channel!')
		return

	game = ctx.channel.name
	game = game.replace('-', '')
	gameid = game.replace("game", "")

	with open('./databases/gamelogs.json') as file:
		gamelogsdata = json.load(file)
		if gamelogsdata[gameid]['voids'] == 0:
			message = await ctx.send(
				"`Game void request submitted! 5/8 players must react before the game is voided!`"
			)
			await message.add_reaction('✅')
			gamelogsdata[gameid]['voidid'] = message.id

			with open('./databases/gamelogs.json', 'w') as updategamelogs:
				json.dump(gamelogsdata, updategamelogs, indent=4)

			timespent = 0

			with open('./databases/voidids.json') as file:
				voidids = json.load(file)

				voidids[gameid] = message.id

				with open('./databases/voidids.json', 'w') as updatevoidids:
					json.dump(voidids, updatevoidids, indent=4)

			return

			await ctx.send(
				f"`Game#{gameid}` has been voided. Closing channels in 15 seconds!"
			)
			textchannel = ctx.channel
			num1 = textchannel.name
			num2 = num1.replace('-', '#')
			num3 = num2.replace('g', 'G')
			num4 = num3 + " | Team "

			callchannel1name = num4 + '1'
			callchannel2name = num4 + '2'

			callchannel1 = discord.utils.get(ctx.guild.channels,
											 name=callchannel1name)
			callchannel2 = discord.utils.get(ctx.guild.channels,
											 name=callchannel2name)

			await callchannel1.delete()
			await callchannel2.delete()
			await textchannel.delete()

		else:
			await ctx.send("There is already an active void request!")


@client.command()
async def pick(ctx, user):
	userid = user.replace("<@", "")
	userid = userid.replace("!", "")
	userid = userid.replace(">", "")
	if str(ctx.channel.category.id) != "949055945005228052":
		await ctx.send("This is not a game channel!")
		return

	with open('./databases/gamelogs.json') as file:
		gamelogsdata = json.load(file)

		game = ctx.channel.name
		game = game.replace('-', '')
		gameid = game.replace("game", "")

		if ctx.author.id not in gamelogsdata[gameid]['captains']:
			await ctx.send("You are not a captain!")
			return

		team = ""
		if ctx.author.id in gamelogsdata[str(
				gameid)]['captains'] and ctx.author.id in gamelogsdata[str(
					gameid)]['team1']:
			team = 1
		elif ctx.author.id in gamelogsdata[str(
				gameid)]['captains'] and ctx.author.id in gamelogsdata[str(
					gameid)]['team2']:
			team = 2

		if team != gamelogsdata[str(gameid)]['pick']:
			await ctx.send("It is not your pick right now!")
			return

		try:
			int(userid)
		except:
			await ctx.send("Please provide a valid ID or @ someone to pick!")
			return

		userid = int(userid)

		if gamelogsdata[gameid]['picksdone'] == True:
			await ctx.send("Picking stage is alread over!")
		else:
			member = ctx.channel.guild.get_member(userid)
			if member == None:
				await ctx.send(
					"You did not pick a valid user! Please @ someone to pick!")
			else:
				with open('./databases/gamelogs.json', 'r') as file:
					gamelogsdata = json.load(file)

					if userid not in gamelogsdata[gameid]['allplayers']:
						await ctx.send("You cannot pick this user!")
						return

					elif userid in gamelogsdata[gameid]['picked']:
						await ctx.send("You cannot pick this user!")
						return

					elif userid in gamelogsdata[gameid]['captains']:
						await ctx.send("You cannot pick this user!")
						return

					else:
						await ctx.send(f"Successfully picked <@{userid}>!")
						gamelogsdata[str(gameid)]['picked'] += [member.id]
						gamelogsdata[str(gameid)][f'team{team}'] += [member.id]

						if gamelogsdata[str(gameid)]['pick'] == 1:
							gamelogsdata[str(gameid)]['pick'] = 2
						elif gamelogsdata[str(gameid)]['pick'] == 2:
							gamelogsdata[str(gameid)]['pick'] = 1

						with open('./databases/gamelogs.json',
								  'w') as updategamelogsdata:
							json.dump(gamelogsdata,
									  updategamelogsdata,
									  indent=4)

						with open('./databases/gamelogs.json', 'r') as file:
							gamelogsdata = json.load(file)

							textchannel = ctx.channel
							num1 = textchannel.name
							num2 = num1.replace('-', '#')
							num3 = num2.replace('g', 'G')
							num4 = num3 + " | Team "

							callchannelname = num4 + 'Pick'
							callchannel1name = num4 + '1'
							callchannel2name = num4 + '2'

							gamecall = discord.utils.get(ctx.guild.channels,
														 name=callchannelname)
							gamecall1 = discord.utils.get(
								ctx.guild.channels, name=callchannel1name)
							gamecall2 = discord.utils.get(
								ctx.guild.channels, name=callchannel2name)

							userspicked = 0
							for player in gamelogsdata[str(gameid)]['picked']:
								userspicked += 1

							if userspicked == 1:
								for userid in gamelogsdata[str(
										gameid)]['team1']:
									userid = int(userid)
									member = ctx.guild.get_member(userid)

									await member.move_to(gamecall1)
									await gamecall1.set_permissions(
										member, connect=True)

								for userid in gamelogsdata[str(
										gameid)]['team2']:
									userid = int(userid)
									member = ctx.guild.get_member(userid)

									await member.move_to(gamecall2)
									await gamecall2.set_permissions(
										member, connect=True)

								await gamecall.delete()


client.run(os.getenv('TOKEN'))
