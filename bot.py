import asyncio
import os
import discord
from igdb.wrapper import IGDBWrapper
import json
import math
from dotenv import load_dotenv
from collections import Counter
from copy import deepcopy

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
IGDB_API_TOKEN = os.getenv('IGDB_API_TOKEN')
ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')
GAME_CHANNEL_ID = os.getenv('GAME_CHANNEL_ID')
GUILD_ID = os.getenv('GUILD_ID')
EMOJI = os.getenv('EMOJI')

intents = discord.Intents().all()

wrapper = IGDBWrapper(CLIENT_ID, IGDB_API_TOKEN)
client = discord.Bot(intents=intents, sync_commands_debug=True, debug_guilds=[GUILD_ID])

os.system('cls' if os.name == 'nt' else 'clear')

requestlist = []
userlist = []
usernamelist = []

@client.event
async def on_ready():
    print("Le bot est en ligne !\n")

@client.command(pass_context=True, description="Demander un nouveau jeu.")
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

    user2 = await client.fetch_user(str(ctx.user.id))
    user3 = await client.fetch_user(ADMIN_USER_ID)

    class View(discord.ui.View):
        @discord.ui.button(emoji="👍", style=discord.ButtonStyle.green, row=1)
        async def first_button_callback(self, button, interaction):
            await user3.send(embed=embed)
            await user2.send("Votre requête a été prise en compte.")
            requestlist.append(game['name'])
            userlist.append(ctx.user.id)
            usernamelist.append(ctx.user.name)
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)
            
        @discord.ui.button(emoji="👎", style=discord.ButtonStyle.red, row=1)
        async def second_button_callback(self, button, interaction):
            await user2.send("Votre requête n'a pas été prise en compte car vous n'avez pas confirmé.")
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)

    await ctx.followup.send(embed=embed, view=View())

@client.command(pass_context=True)
async def list(ctx):
    embed = discord.Embed(
        title="Liste des requêtes :",
        color=10181046,
        description=str(requestlist).replace("[", "").replace("]", "").replace("'", "")
    )
    await ctx.respond(embed=embed)

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

    await ctx.respond("Quelle est la taille du fichier ?")
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

    class View(discord.ui.View):
        @discord.ui.button(label="Télécharger le jeu", url=url, style=discord.ButtonStyle.green, row=1)
        async def first_button_callback(interaction, self):
            await interaction.response.edit_message(view=self)
        @discord.ui.button(label="Plus d'informations", url=game_url, style=discord.ButtonStyle.grey, row=1)
        async def first_button_callback(interaction, self):
            await interaction.response.edit_message(view=self)
    
    await channel.send(embed=embed, view=View())
    requestlist.remove(jeu)


#StromCoin economy from here

balance_dict = {}

#add user to balance_dict if not already there and if not a bot
async def add_user(user):
    if user.id not in balance_dict and not user.bot:
        balance_dict[user.id] = 0

@client.command(pass_context=True)
async def balance(ctx):
    await add_user(ctx.author)
    user = ctx.author
    user_id = user.id
    user_name = user.name
    user_balance = balance_dict[user_id]
    embed = discord.Embed(
        title = f"Votre solde :",
        color=10181046,
        description=f"**Solde :**\n```{user_balance}```{EMOJI}"
    )
    await ctx.respond(embed=embed)


@client.command(pass_context=True)
async def pay(ctx, user: discord.User, amount: int):
    await add_user(ctx.author)
    await add_user(user)
    user_id = user.id
    user_name = user.name
    user_balance = balance_dict[user_id]
    if amount > user_balance:
        await ctx.respond("Vous n'avez pas assez d'argent.")
    else:
        balance_dict[user_id] = user_balance - amount
        balance_dict[ctx.author.id] = balance_dict[ctx.author.id] + amount
        await ctx.respond(f"Vous avez payé {user_name} {amount} {EMOJI}.")
        replace_user_id(user)

#replace user id in balance_dict with user name
baltop_dict = deepcopy(balance_dict)
async def replace_user_id(user):
    user_id = user.id
    user_name = user.name
    baltop_dict[user_name] = balance_dict[user_id]
    sorted(baltop_dict, key=baltop_dict.get, reverse=True)


@client.command(pass_context=True)
async def give(ctx, user: discord.User, amount: int):
    await add_user(user)
    if ctx.author.id == int(ADMIN_USER_ID):
        user_id = user.id
        user_name = user.name
        user_balance = balance_dict[user_id]
        balance_dict[user_id] = user_balance + amount
        await ctx.respond(f"Vous avez donné à {user_name} {amount} {EMOJI}.")
        await replace_user_id(user)
    else:
        await ctx.respond("Vous n'avez pas les droits.")

#create a /baltop command 
@client.command(pass_context=True)
async def baltop(ctx):
    sorted(baltop_dict, key=baltop_dict.get, reverse=True)
    await add_user(ctx.author)
    await replace_user_id(ctx.author)
    embed = discord.Embed(
        title = "Liste des StromJoueurs les plus riches :",
        color=10181046,
        description="**Top des joueurs :**\n```" + str(baltop_dict).replace('{', '').replace('}', '').replace('\'', '').replace(', ', '\n')+ "```"
    )
    await ctx.respond(embed=embed)

#create SHOP_LIST
SHOP_LIST = {}

#create a /shop command
@client.command(pass_context=True)
async def shop(ctx):
    embed = discord.Embed(
        title = "Boutique :",
        color=10181046,
    )
    for item in SHOP_LIST:
        prix = SHOP_LIST[item]["prix"]
        description = SHOP_LIST[item]["description"]
        embed.add_field(name=item, value=f"prix : **{prix}** {EMOJI}\n{description}\n", inline=False)
    await ctx.respond(embed=embed)

#create a /buy command and when an item is bought add it to their inventory
@client.command(pass_context=True)
async def buy(ctx, item: str):
    await add_user(ctx.author)
    user_id = ctx.author.id
    user_balance = balance_dict[user_id]
    if item in SHOP_LIST:
        if user_balance >= SHOP_LIST[item]["prix"]:
            balance_dict[user_id] = user_balance - SHOP_LIST[item]["prix"]
            await ctx.respond(f"Vous avez acheté **{item}** pour {SHOP_LIST[item]['prix']} {EMOJI}.")
            await replace_user_id(ctx.author)
        else:
            await ctx.respond("Vous n'avez pas assez d'argent.")
    else:
        await ctx.respond("Cet item n'existe pas.")

#create a /add command and add an item to the shop list
@client.command(pass_context=True)
async def add(ctx, item: str, prix: int, description: str):
    if ctx.author.id == int(ADMIN_USER_ID):
        SHOP_LIST[item] = {
            "prix": prix,
            "description": description
        }
        await ctx.respond("L'item a été ajouté à la boutique.")
    else:
        await ctx.respond("Vous n'avez pas les droits.")

#give 2 coins for every message
@client.event
async def on_message(message):
    await add_user(message.author)
    user_id = message.author.id
    balance_dict[user_id] = balance_dict[user_id] + 2
    await replace_user_id(message.author)

#create a salary function that gives 50 coins every 7 days
async def salary():
    await client.wait_until_ready()
    while not client.is_closed():
        for user in balance_dict:
            balance_dict[user] = balance_dict[user] + 50
        await asyncio.sleep(604800)

#create a badass_salary function that gives 50 coins every 7 days to member with StromBadass role
async def badass_salary(message):
    await client.wait_until_ready()
    while not client.is_closed():
        for user in balance_dict:
            if discord.utils.get(message.author.roles, name="StromBadass") is not None:
                balance_dict[user] = balance_dict[user] + 50
        await asyncio.sleep(604800)

#create a /remove command that can only be used by admins and remove an item from the shop list
@client.command(pass_context=True)
async def remove(ctx, item: str):
    if ctx.author.id == int(ADMIN_USER_ID):
        if item in SHOP_LIST:
            del SHOP_LIST[item]
            await ctx.respond("L'item a été retiré de la boutique.")
        else:
            await ctx.respond("Cet item n'existe pas.")
    else:
        await ctx.respond("Vous n'avez pas les droits.")

client.run(BOT_TOKEN)