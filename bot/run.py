import discord
import requests
from discord.ext import commands
import sqlite3
conn = sqlite3.connect('bot.db')
import json
import asyncio

YEAR_GROUPS = ['9M', '9S', '10M', '10S', '11']
ROLES_TO_REMOVE = ['Year 9', 'Year 10', 'Year 11', 'Marlowe', 'Shakespeare', '10 Marlowe', '10 Shakespeare', '9 Marlowe', '9 Shakespeare']
YEAR_ROLES = {
    '9M':['Year 9', 'Marlowe', '9 Marlowe'],
    '9S':['Year 9', 'Shakespeare', '9 Shakespeare'],
    '10M':['Year 10', 'Marlowe', '10 Marlowe'],
    '10S':['Year 10', 'Shakespeare', '10 Shakespeare'],
    '11':['Year 11']
}
GROUP_IDS = {
    '9M': '26857770',
    '9S': '26857768',
    '10M': '26857755',
    '10S': '26857761',
    '11': '26857752'
}
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

    req = None

    message = await bot.get_channel(801846950147391558).fetch_message(payload.message_id)

    if message == None:
        return

    for reqLog in data['yearChangeQueue']:
        if reqLog['messageId'] == payload.message_id:
            req = reqLog

    if req == None:
        for reqLog in data['nameChangeQueue']:
            if reqLog['messageId'] == payload.message_id:
                req = reqLog

    if req == None:
        await error(message.channel, 'An error occurred. Please report this.\n`messageId not found.`')
        return

    if str(payload.emoji) == '❎':
        if message.embeds[0].title == 'New Year Group Request!':
            embed = discord.Embed(title = 'Year Group Request Denied', description = '*This request has been denied by a member of SLT.*', color = 0xFF6961)
            embed.add_field(name = 'RBX ID', value = req['rbxId'], inline = True)
            embed.add_field(name = 'Year Requested', value = req['yearGroup'].upper(), inline = True)
            
            await message.edit(embed = embed)

            user = await bot.fetch_user(req['discordId'])
            if user == None:
                await error(message.channel, 'User not found. Notification not sent.')
                return

            embed = discord.Embed(title = 'Year Group Request Denied', description = 'Your year group request was denied by a member of SLT!', color = 0xFF6961)
            await user.send(embed = embed)

            await message.clear_reactions()
            data['yearChangeQueue'].remove(req)
            #for k, v in data.items():
            #    if v == reqLog:
            #        del data[k]
            with open('data.json', 'w') as f:
                json.dump(data, f, indent=4)

        elif message.embeds[0].title == 'New Name Change Request!':
            embed = discord.Embed(title = 'Name Change Request Denied', description = '*This request has been denied by a member of SLT.*', color = 0xFF6961)
            embed.add_field(name = 'Discord ID', value = req['discordId'], inline = True)
            embed.add_field(name = 'Name Requested', value = req['nameRequested'])

            await message.edit(embed = embed)

            user = await bot.fetch_user(req['discordId'])
            if user == None:
                await error(message.channel, 'User not found. Notification not sent.')
                return
            
            embed = discord.Embed(title = 'Name Change Request Denied', description = 'Your year group request was denied by a member of SLT!', color = 0xFF6961)
            await user.send(embed = embed)

            await message.clear_reactions()
            data['nameChangeQueue'].remove(req)
            with open('data.json', 'w') as f:
                json.dump(data, f, indent=4)

    elif str(payload.emoji) == '✅':
        if message.embeds[0].title == 'New Year Group Request!':
            embed = discord.Embed(title = 'Year Group Request Accepted', description = '*This request has been accepted by a member of SLT.*', color = 0x77DD77)
            embed.add_field(name = 'RBX ID', value = req['rbxId'], inline=True)
            embed.add_field(name = 'Year Requested', value = req['yearGroup'].upper(), inline = True)

            await message.edit(embed = embed)

            user = await bot.fetch_user(req['discordId'])
            if user == None:
                await error(message.channel, 'User not found. Notification not sent.')
            else:
                embed = discord.Embed(title = 'Year Group Request Accepted', description = 'Your year group request was accepted by a member of SLT!', color = 0x77DD77)
                await user.send(embed = embed)

                member = await bot.get_guild(743642257080451193).fetch_member(user.id)

                if member == None:
                    await error(message.channel, 'Member not found. Auto-role not possible.\n`get_member returned None.`')
                else:
                    for role in member.roles:
                        if role.name in ROLES_TO_REMOVE:
                            await member.remove_roles(role, reason = 'Change year request')
                    
                    for role in YEAR_ROLES[req['yearGroup'].upper()]:
                        await member.add_roles(discord.utils.get(bot.get_guild(743642257080451193).roles, name=role), reason = 'Change year request')

                url = "https://auth.roblox.com/v2/login"

                payload="{}"
                headers = {
                    'Content-Type': 'application/json',
                    'Cookie': 'GuestData=UserID=-606985113; RBXEventTrackerV2=CreateDate=1/22/2021 8:34:08 AM&rbxid=&browserid=77093773054; .ROBLOSECURITY=_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_69B2C9C148577AC408DE17A0DAB177C230FEF360A127EA9792C8DAADEF30E4013ABA4079081FBBDE10FF5F57F8709C54DB74C951F6FA2639C92A542C5AD72B4DCCDD9F2E683E5881A35EF96770C4C1A89F45E20D7E26680E7C0830630376C3FC0BC3CE525280D1A4C508A4803AC1F27F14549DEA0B900FA4568329D20BCDDDEC958E2EF101E85C839E4943F6B8204066633EC65C42E7FDFBF7A3052E95C965BB536189B1C15753AF334E321E07E5740B5BAE26A53721DFDEF87CE217DD58018B39F0784048ECEE53F88BCFDE92E5E2843313C864F2F6C8D14B10C8F618E462D519CFD2166465A436D1C2371A2FED4B9C4F1C3640938E1B3B1D32DB4BD785AA0F7323BD75A30F6B9C1CBA1CB2346FDB047B5F4137625524485B72261C66CD4BADFE440A64; .RBXID=_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJmMDNjOGZiMC1jMWQ4LTRjZjktYTk4Ny1jYThkMjMyODU5YjUiLCJzdWIiOjk0MzMyMTkzOX0.jEfimXZproU8LVTl8GhrXXnwE-PxLGv65VoVXCSL4j0'
                }

                response = requests.request("POST", url, headers=headers, data=payload)

                token = response.headers['x-csrf-token']

                with open('config.json', 'r+') as f:
                    config = json.load(f)
                    user = config['user']
                    password = config['password']
                    cookie = config['cookie']

                payload="{\r\n    \"ctype\": \"username\",\r\n    \"cvalue\": \""+user+"\",\r\n    \"password\": \""+password+"\",\r\n    \".ROBLOSECURITY\": \""+cookie+"\"\r\n}"
                headers = {
                    'x-csrf-token': token,
                    'Content-Type': 'application/json',
                    'Cookie': 'GuestData=UserID=-606985113; RBXEventTrackerV2=CreateDate=1/22/2021 8:34:08 AM&rbxid=&browserid=77093773054; .ROBLOSECURITY=_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_69B2C9C148577AC408DE17A0DAB177C230FEF360A127EA9792C8DAADEF30E4013ABA4079081FBBDE10FF5F57F8709C54DB74C951F6FA2639C92A542C5AD72B4DCCDD9F2E683E5881A35EF96770C4C1A89F45E20D7E26680E7C0830630376C3FC0BC3CE525280D1A4C508A4803AC1F27F14549DEA0B900FA4568329D20BCDDDEC958E2EF101E85C839E4943F6B8204066633EC65C42E7FDFBF7A3052E95C965BB536189B1C15753AF334E321E07E5740B5BAE26A53721DFDEF87CE217DD58018B39F0784048ECEE53F88BCFDE92E5E2843313C864F2F6C8D14B10C8F618E462D519CFD2166465A436D1C2371A2FED4B9C4F1C3640938E1B3B1D32DB4BD785AA0F7323BD75A30F6B9C1CBA1CB2346FDB047B5F4137625524485B72261C66CD4BADFE440A64; .RBXID=_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJmMDNjOGZiMC1jMWQ4LTRjZjktYTk4Ny1jYThkMjMyODU5YjUiLCJzdWIiOjk0MzMyMTkzOX0.jEfimXZproU8LVTl8GhrXXnwE-PxLGv65VoVXCSL4j0'
                }

                response = requests.request("POST", url, headers=headers, data=payload)

                if not 'user' in json.loads(response.text):
                    await error(message.channel, 'Bot login failed. Manual group rank required.\n`Auth request returned user None.`')
                else:
                    url = "https://groups.roblox.com/v1/groups/3950286/users/"+str(req['rbxId'])

                    payload="{\r\n\t\"roleId\": "+GROUP_IDS[req['yearGroup'].upper()]+"\r\n}"
                    headers = {
                        'x-csrf-token': token,
                        'Content-Type': 'application/json',
                        'Cookie': 'GuestData=UserID=-606985113; .ROBLOSECURITY=_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_69B2C9C148577AC408DE17A0DAB177C230FEF360A127EA9792C8DAADEF30E4013ABA4079081FBBDE10FF5F57F8709C54DB74C951F6FA2639C92A542C5AD72B4DCCDD9F2E683E5881A35EF96770C4C1A89F45E20D7E26680E7C0830630376C3FC0BC3CE525280D1A4C508A4803AC1F27F14549DEA0B900FA4568329D20BCDDDEC958E2EF101E85C839E4943F6B8204066633EC65C42E7FDFBF7A3052E95C965BB536189B1C15753AF334E321E07E5740B5BAE26A53721DFDEF87CE217DD58018B39F0784048ECEE53F88BCFDE92E5E2843313C864F2F6C8D14B10C8F618E462D519CFD2166465A436D1C2371A2FED4B9C4F1C3640938E1B3B1D32DB4BD785AA0F7323BD75A30F6B9C1CBA1CB2346FDB047B5F4137625524485B72261C66CD4BADFE440A64; .RBXID=_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJmMDNjOGZiMC1jMWQ4LTRjZjktYTk4Ny1jYThkMjMyODU5YjUiLCJzdWIiOjk0MzMyMTkzOX0.jEfimXZproU8LVTl8GhrXXnwE-PxLGv65VoVXCSL4j0; RBXSource=rbx_acquisition_time=1/23/2021 8:37:47 AM&rbx_acquisition_referrer=&rbx_medium=Direct&rbx_source=&rbx_campaign=&rbx_adgroup=&rbx_keyword=&rbx_matchtype=&rbx_send_info=1; RBXEventTrackerV2=CreateDate=1/23/2021 8:37:47 AM&rbxid=2315340398&browserid=77093773054'
                    }

                    response = requests.request("PATCH", url, headers=headers, data=payload)

                    if 'errors' in json.loads(response.text):
                        await error(message.channel, 'Group ranking failed.\n`PATCH request returned error.`')

            await message.clear_reactions()
            data['yearChangeQueue'].remove(req)
            #for k, v in data.items():
            #    if v == reqLog:
            #        del data[k]
            with open('data.json', 'w') as f:
                json.dump(data, f, indent=4)

        elif message.embeds[0].title == 'New Name Change Request!':
            embed = discord.Embed(title = 'Name Change Request Accepted', description = '*This request has been accepted by a member of SLT.*', color = 0x77DD77)
            embed.add_field(name = 'Discord ID', value = req['discordId'], inline=True)
            embed.add_field(name = 'Name Requested', value = req['nameRequested'], inline = True)

            await message.edit(embed = embed)

            user = await bot.fetch_user(req['discordId'])
            if user == None:
                await error(message.channel, 'User not found. Notification not sent.')
            else:
                embed = discord.Embed(title = 'Name Change Request Accepted', description = 'Your name change request was accepted by a member of SLT!', color = 0x77DD77)
                await user.send(embed = embed)

                member = await bot.get_guild(743642257080451193).fetch_member(user.id)

                if member == None:
                    await error(message.channel, 'Member not found. Nick not possible.\n`get_member returned None.`')
                else:
                    url = 'https://users.roblox.com/v1/users/{}'.format(req['rbxId'])
                    r = requests.get(url)
                    response = json.loads(r.text)
                    userName = response['displayName']
                    newNick = req['nameRequested'] + ' - ' + userName
                    await member.edit(nick = newNick, reason = 'Change name request')

            await message.clear_reactions()
            data['nameChangeQueue'].remove(req)
            with open('data.json', 'w') as f:
                json.dump(data, f, indent=4)

    



@bot.command()
async def changeyear(ctx, arg):
    #if not ctx.author.id == 302471371319934997:
        #return

    if not arg.upper() in YEAR_GROUPS:
        await error(ctx, 'Invalid year group. Please try again.')
        return

    url = 'https://api.blox.link/v1/user/{}?guild=743642257080451193'.format(str(ctx.author.id))
    r = requests.get(url)
    response = json.loads(r.text)

    if response['status'] == 'error':
        await error(ctx, 'An error occurred. Please report this and try again.\n`API call returned bad response.`')
        return

    robloxId = response['matchingAccount']
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
    embed.add_field(name = 'Year Requested', value = arg.upper(), inline = False)
    embed.set_footer(text = FOOTER)

    reqMsg = await channels['adminRequests'].send(embed = embed)
    with open('data.json', 'r') as f:
        data = json.load(f)

    newData = {'messageId':reqMsg.id, 'discordId':ctx.author.id, 'rbxId':robloxId, 'yearGroup':arg.upper()}
    data['yearChangeQueue'].append(newData)

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

    await reqMsg.add_reaction('✅')
    await reqMsg.add_reaction('❎')

    await success(ctx, 'Request submitted succesfully! You\'ll receive a message once your request is updated!')

    #{ "status": "ok", "primaryAccount": "569422833", "matchingAccount": null }
    #{ "status": "error", "error": "This user is not linked to Bloxlink." }

@bot.command()
async def changename(ctx, arg, arg2):
    arg = arg + ' ' + arg2
    arg = arg.title()

    url = 'https://api.blox.link/v1/user/{}?guild=743642257080451193'.format(str(ctx.author.id))
    r = requests.get(url)
    response = json.loads(r.text)

    if response['status'] == 'error':
        await error(ctx, 'An error occured. Please report this and try again.\n`API call returned bad response.`')
        return

    robloxId = response['matchingAccount']
    url = 'https://users.roblox.com/v1/users/{}'.format(robloxId)
    r = requests.get(url)
    response = json.loads(r.text)
    userName = response['displayName']

    embed = discord.Embed(title = 'New Name Change Request!', description = 'A user has requested to change their name!', color = 0x2693FF)
    embed.add_field(name = 'Username', value = userName, inline = True)
    embed.add_field(name = 'RBX ID', value = robloxId, inline = True)
    embed.add_field(name = '\u200b', value = '\u200b', inline = True)
    embed.add_field(name = 'Current Nickname', value = ctx.author.nick, inline = True)
    embed.add_field(name = 'Discord ID', value = ctx.author.id, inline = True)
    embed.add_field(name = '\u200b', value = '\u200b', inline = True)
    embed.add_field(name = 'Name Requested', value = arg, inline = False)
    embed.set_footer(text = FOOTER)

    reqMsg = await channels['adminRequests'].send(embed = embed)
    with open('data.json', 'r') as f:
        data = json.load(f)

    newData = {'messageId':reqMsg.id, 'discordId':ctx.author.id, 'rbxId':robloxId, 'nameRequested':arg}
    data['nameChangeQueue'].append(newData)

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

    await reqMsg.add_reaction('✅')
    await reqMsg.add_reaction('❎')

    await success(ctx, 'Request submitted succesfully! You\'ll receive a message once your request is updated!')

with open('config.json') as f:
    bot.run(json.load(f)['token'])