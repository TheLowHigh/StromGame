import os
import discord
from discord.ext import commands
from igdb.wrapper import IGDBWrapper
import json
import math
from discord.ui import Button, View

wrapper = IGDBWrapper("CLIENT_ID", "IGDB_API_TOKEN")
intents = discord.Intents().all()
client = commands.Bot(command_prefix="!", intents=intents, sync_commands_debug=True)

os.system('cls' if os.name == 'nt' else 'clear')

requestlist = []
userlist = []
usernamelist = []
emoji_yes = '✅'
emoji_no = '❌'

@client.event
async def on_ready():
    print("Le bot est en ligne !\n")

@client.slash_command(pass_context=True, description="Demander un nouveau jeu.")
async def request(ctx, *, search):
    await ctx.defer(invisible=False)
    try:
        byte_array = wrapper.api_request(
            'games',
            'fields *; search "' + search + '"; limit 1;',
          )
        game_response=json.loads(byte_array)
        for game in game_response:
            nom = game['name']
            game_url = game['url']
            art_id = game['cover']
            platform_id = game['platforms']
            genre_id = game['genres']
            rating = game['aggregated_rating']
    except:
        pass

    try:
        byte_array2 = wrapper.api_request(
            'covers',
            'fields *; where id = ' + str(art_id) + '; limit 1;',
          )
        art_respone=json.loads(byte_array2)
        for artwork in art_respone:
                art = artwork['url']
                art = art.replace("thumb", "1080p")
    except:
        pass
    
    try:
        byte_array3 = wrapper.api_request(
            'platforms',
            'fields *; where id = ' + str(platform_id).replace("[", "(").replace("]", ")") + ';'
          )
        platform_response=json.loads(byte_array3)
        all_platforms = []
        for platform in platform_response:
            all_platforms.append(platform['name'])
    except:
        pass

    try:
        byte_array4 = wrapper.api_request(
            'genres',
            'fields *; where id = ' + str(genre_id).replace("[", "(").replace("]", ")") + ';'
          )
        genre_response=json.loads(byte_array4)
        all_genres = []
        for genre in genre_response:
            all_genres.append(genre['name'])
    except:
        pass

    try:
        embed = discord.Embed(
            title=f"Le jeu {nom} a été trouvé", url = game_url,
            color=10181046,
            description=f"**Nom**\n```{nom}```"
            )
    except:
        await ctx.send("Le jeu demandé n'a pas été trouvé, avez-vous vérifié l'orthographe ? Si c'est le cas et que l'erreur persiste vous pouvez faire votre requête à l'administrateur.")

    try:
        platforms = str(all_platforms).replace("[", "").replace("]", "").replace("'", "")
    except:
        pass
    try:
        genres = str(all_genres).replace("[", "").replace("]", "").replace("'", "")
    except:
        pass

    try:
        embed.add_field(name="**Plateforme(s)**",value=f"```{platforms}```")
    except:
        pass

    try:
        embed.add_field(name="**Genre(s)**",value=f"```{genres}```")
    except:
        pass

    try:
        embed.add_field(name="**Note**",value=f"```{math.floor(rating)}/100```")
    except:
        pass

    try:
        embed.set_image(url="https:"+art)
    except:
        pass
    
    button1 = Button(emoji="👍", style=discord.ButtonStyle.green, row=1)
    button2 = Button(emoji="👎", style=discord.ButtonStyle.red, row=1)

    user2 = await client.fetch_user(str(ctx.user.id))

    async def button_callback(interaction):
        user3 = await client.fetch_user("389088767132041226")
        await user3.send(embed=embed)
        await user2.send("Votre requête a été prise en compte.")
        requestlist.append(game['name'])
        userlist.append(ctx.user.id)
        usernamelist.append(ctx.user.name)
        await interaction.response.edit_message(content=None)
    button1.callback = button_callback

    async def button_callback2(interaction):
        await user2.send("Votre requête n'a pas été prise en compte car vous n'avez pas confirmé.")
        await interaction.response.edit_message(content=None)


    button2.callback = button_callback2

    view = View()
    view.add_item(button1)
    view.add_item(button2)
    await ctx.followup.send(embed=embed, view=view)

@client.slash_command(pass_context=True)
async def list(ctx):
    embed = discord.Embed(
        title="Liste des requêtes :",
        color=10181046,
        description=str(requestlist).replace("[", "").replace("]", "").replace("'", "")
    )
    await ctx.send(embed=embed)

@client.slash_command(pass_context=True)
async def fill(ctx):
    current_channel = ctx.channel

    def check(m):
        return m.channel == current_channel

    await ctx.send("Choissisez un jeu :\n" + str(requestlist).replace("[", "").replace("]", "").replace("'", ""))
    msg = await client.wait_for('message', check=check, timeout=60)
    jeu = msg.content

    await ctx.send(f"Choissisez un utilisateur (entrez l'id):\n" + str(usernamelist).replace("[", "").replace("]", "").replace("'", "") + "\n" + str(userlist).replace("[", "").replace("]", "").replace("'", ""))
    msg = await client.wait_for('message', check=check, timeout=60)
    user = await client.fetch_user(msg.content)

    await ctx.send("Quelle est l'url ?")
    msg = await client.wait_for('message', check=check, timeout=60)
    url = msg.content

    await ctx.send("Quelle est la taille du fichier ?")
    msg = await client.wait_for('message', check=check, timeout=60)
    taille = msg.content
    
    embed = discord.Embed(
        title = f"Votre requête pour {jeu} est disponible !",
        color=10181046,
        description=f"**Lien de téléchargement :**\n{url}\n **Taille :**\n```{taille}```\n"
    )
    await user.send(embed=embed)
    channel = client.get_channel(GAME_CHANNEL_ID)

    try:
        byte_array = wrapper.api_request(
            'games',
            'fields *; search "' + jeu + '"; limit 1;',
          )
        game_response=json.loads(byte_array)
        for game in game_response:
            nom = game['name']
            game_url = game['url']
            art_id = game['cover']
            platform_id = game['platforms']
            genre_id = game['genres']
            rating = game['aggregated_rating']
    except:
        pass

    try:
        byte_array2 = wrapper.api_request(
            'covers',
            'fields *; where id = ' + str(art_id) + '; limit 1;',
          )
        art_respone=json.loads(byte_array2)
        for artwork in art_respone:
                art = artwork['url']
                art = art.replace("thumb", "1080p")
    except:
        pass

    try:
        embed.set_image(url="https:"+art)
    except:
        pass

    button1 = Button(label="Télécharger le jeu", url=url, style=discord.ButtonStyle.green, row=1)
    button2 = Button(label="Plus d'informations", url=game_url, style=discord.ButtonStyle.grey, row=1)
    view = View()
    view.add_item(button1)
    view.add_item(button2)

    await channel.send(embed=embed, view=view)
    requestlist.remove(jeu)



client.run("TOKEN")