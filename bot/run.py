import discord
import requests
from discord.ext import commands
import sqlite3
conn = sqlite3.connect('bot.db')
import json
import asyncio

YEAR_GROUPS = ['9M', '9S', '10M', '10S', '11']
INITIAL_EXTENSIONS = []
FOOTER = ''
channels = {}

bot = commands.Bot(command_prefix = commands.when_mentioned_or('a!'), help_command = None, description = None)

#FOOTER = '{}help | discord.gg/cdTPzmy'.format(get_prefix)]

async def error(ctx, message):
    embed = discord.Embed(title = 'Error!', description = message, color=0xFF6961)
    embed.set_footer(text = FOOTER)
    await ctx.send(embed = embed)

async def success(ctx, message):
    embed = discord.Embed(title = 'Success!', description = message, color=0x77DD77)
    embed.set_footer(text = FOOTER)
    await ctx.send(embed=embed)

# Here we load our extensions(cogs) listed above in [initial_extensions].
#if __name__ == '__main__':
    #for extension in INITIAL_EXTENSIONS:
        #bot.load_extension(extension)

@bot.event
async def on_ready():
    """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""

    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')

    # Changes our bots Playing Status.
    activity = discord.Activity(name = 'rj code me', type=discord.ActivityType.watching)
    await bot.change_presence(status=discord.Status.idle, activity=activity)
    print('Successfully logged in and booted...!')

    channels['adminRequests'] = bot.get_channel(801846950147391558)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    with open('data.json', 'r') as f:
        data = json.load(f)

    
    

@bot.command()
async def changeyear(ctx, arg):
    if not ctx.author.id == 302471371319934997:
        return

    if not arg in YEAR_GROUPS:
        await error(ctx, 'Invalid year group. Please try again.')
        return

    url = 'https://api.blox.link/v1/user/{}'.format(str(ctx.author.id))
    r = requests.get(url)
    response = json.loads(r.text)

    if response['status'] == 'error':
        await error(ctx, 'An error occured. Please report this and try again.\n`API call returned bad response.`')
        return

    robloxId = response['primaryAccount']
    url = 'https://users.roblox.com/v1/users/{}'.format(robloxId)
    r = requests.get(url)
    response = json.loads(r.text)
    userName = response['displayName']

    embed = discord.Embed(title = 'New Year Group Request!', description = 'A user has requested to change year groups!', color = 0x2693FF)
    embed.add_field(name = 'Username', value = userName, inline = True)
    embed.add_field(name = 'RBX ID', value = robloxId, inline = True)
    embed.add_field(name = '\u200b', value = '\u200b', inline = True)
    embed.add_field(name = 'Nickname', value = ctx.author.nick, inline = True)
    embed.add_field(name = 'Discord ID', value = ctx.author.id, inline = True)
    embed.add_field(name = '\u200b', value = '\u200b', inline = True)
    embed.add_field(name = 'Year Requested', value = arg, inline = False)
    embed.set_footer(text = FOOTER)

    reqMsg = await channels['adminRequests'].send(embed = embed)
    with open('data.json', 'r') as f:
        data = json.load(f)
        print(data)

    newData = {'messageId':reqMsg.id, 'discordId':ctx.author.id, 'rbxId':robloxId, 'yearGroup':arg}
    data['yearChangeQueue'].append(newData)

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

    await reqMsg.add_reaction('✅')
    await reqMsg.add_reaction('❎')

    await success(ctx, 'Request submitted succesfully! You\'ll receive a message once your request is updated!')

    #{ "status": "ok", "primaryAccount": "569422833", "matchingAccount": null }
    #{ "status": "error", "error": "This user is not linked to Bloxlink." }

with open('config.json') as f:
    bot.run(json.load(f)['token'])