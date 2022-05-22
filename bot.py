import discord
import os
from discord.ext import commands
from igdb.wrapper import IGDBWrapper
import json

wrapper = IGDBWrapper("IGDB_CLIENT_ID", "IGDB_APP_TOKEN")
client = commands.Bot(command_prefix="$")

os.system('cls' if os.name == 'nt' else 'clear')

@client.event
async def on_ready():
    print("Le bot est en ligne !\n")

@client.command(aliases=["request"], pass_context=True)
async def showpic(ctx, *, search):

    byte_array = wrapper.api_request(
            'games',
            'fields *; search "' + search + '"; limit 1;',
          )
    game_respone=json.loads(byte_array)
    for game in game_respone:
        nom = (game['name'])
        game_url = (game['url'])
        art_id = (game['artworks'][2])

    byte_array2 = wrapper.api_request(
            'artworks',
            'fields url; where id = ' + str(art_id) + '; limit 1;',
          )
    art_respone=json.loads(byte_array2)
    for artwork in art_respone:
            art = (artwork['url'])

    embed1 = discord.Embed(
        title=f"Le jeu {nom} a bien été demandé", url = game_url,
        color=10181046,
        description="**Nom**\n" + "```" + nom + "```", inline=True
        )
    embed1.set_image(url="https:"+art)
    await ctx.send(embed=embed1)


client.run("TOKEN")