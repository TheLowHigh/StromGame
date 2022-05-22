import discord
import os
from discord.ext import commands
from igdb.wrapper import IGDBWrapper
import json
import asyncio

wrapper = IGDBWrapper("CLIENT_ID", "IGDB_API_TOKEN")
intents = discord.Intents().all()
client = commands.Bot(command_prefix="$", intents=intents)

os.system('cls' if os.name == 'nt' else 'clear')

requestlist = []
userlist = []
usernamelist = []

@client.event
async def on_ready():
    print("Le bot est en ligne !\n")

@client.command(pass_context=True)
async def request( ctx, *, search):

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

    embed = discord.Embed(
        title=f"Le jeu {nom} a été trouvé", url = game_url,
        color=10181046,
        description=f"**Nom**\n```{nom}```"
        )

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
        embed.set_image(url="https:"+art)
    except:
        pass
    
    
    message = await ctx.send(embed=embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '✅'
    user2 = await client.fetch_user(ctx.message.author.id)
    try:
        if user == ctx.author and str(reaction.emoji) == '❌':
            await user2.send("Votre requête n'a pas été prise en compte car le jeu est incorrect.")
        reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await user2.send("Votre requête n'a pas été prise en compte car vous n'avez pas confirmé.")
    
    user3 = await client.fetch_user("ADMIN_USER_ID")
    await user3.send(embed=embed)
    user2.send("Votre requête a été prise en compte.")
    requestlist.append(game['name'])
    userlist.append(ctx.message.author.id)
    usernamelist.append(ctx.author.name)

@client.command(pass_context=True)
async def list(ctx):
    embed = discord.Embed(
        title="Liste des requêtes :",
        color=10181046,
        description=str(requestlist).replace("[", "").replace("]", "").replace("'", "")
    )
    await ctx.send(embed=embed)

@client.command(pass_context=True)
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
    await channel.send(embed=embed)
    requestlist.remove(jeu)



client.run("TOKEN")