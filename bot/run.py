import discord
from discord.ext import commands

async def get_prefix():
    # More to be added to this with config options etc, will remain like this for now
    return 'a!'

bot = commands.Bot(command_prefix = commands.when_mentioned_or(get_prefix()), help_command = None, description = None)