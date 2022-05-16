from discord import Client, Intents, Embed
from discord_slash import SlashCommand, SlashContext
from discord_components import *
import imdb
import os
from discord_slash.utils.manage_commands import create_option

ia = imdb.IMDb()
bot = Client(intents=Intents.default())
slash = SlashCommand(bot, sync_commands = True)

os.system('cls' if os.name == 'nt' else 'clear')

@bot.event
async def on_ready():
    print("Ready !")

@slash.slash(name="request", guild_ids=[915349367773351997], description="Demander un nouveau jeu.", options=[
    create_option(name="jeu", description="Nom du jeu.", option_type=3, required=True)
])
async def request(ctx: SlashContext, jeu = 1):
    embed = Embed(
    title="Votre jeu à bien été demandé",
    description='Nom : '+ jeu,
    color=10181046,
    )
    await ctx.send(embed=embed)
        
    
bot.run("token")
