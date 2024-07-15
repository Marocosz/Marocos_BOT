import discord
from discord.ext import commands
import random
import asyncio
import requests
import datetime
import backfunctions as bf
import subprocess

TOKEN_Riot = ""
TOKEN_Discord = ""

# Configurando as permissões do BOT
permitions = discord.Intents.default()
permitions.message_content = True
permitions.members = True
permitions.reactions = True

# Definindo o BOT e seu prefixo
bot = commands.Bot(command_prefix=".", intents=permitions)

# Função 'Evento' ao entrar membro
@bot.event
async def on_member_join(membro:discord.Member):
    channel = bot.get_channel(1009289951474614323)
    await channel.send(f'{membro.mention} Mais um fudido kkkkkkkkkkkkk')

# Função 'Evento' ao sair/expulsado membro
@bot.event
async def on_member_remove(membro:discord.Member):
    channel = bot.get_channel(1009289951474614323)
    await channel.send(f'{membro.display_name} Não aguentou ser fudido kkkkkkkkkkkk')

# Função 'Comando' de divisão de duas equipes as quais reagirão a mensagem do BOT
@bot.command()
async def dividir(ctx):
    wait_time = 30

    # Embed e suas determinações
    embed_split = discord.Embed(
        title="⚪ Divisão de Times Personalizada",
        description=f"📩 Reaja para entrar no sorteio de times!\n\n⏰ Aguarde {wait_time} segundos para que todos possam reagir...\n\n📋 Aleatorizando Equipes",
        color=0x00b0f4
    )

    img_embed_split = discord.File('imgs/ligadaslendas.jpg', 'ligadaslendas.jpg')
    embed_split.set_image(url='attachment://ligadaslendas.jpg')

    thum_embed_split = discord.File('imgs/ligadaslendas.jpg', 'ligadaslendas.jpg')
    embed_split.set_thumbnail(url='attachment://ligadaslendas.jpg')

    icon_author = discord.File('imgs/icon.jpg', 'icon.jpg')
    embed_split.set_author(name="Marocos BOT", icon_url="attachment://icon.jpg")

    embed_split.set_footer(text="Discord")

    message = await ctx.reply(files=[thum_embed_split, icon_author], embed=embed_split)
    await message.add_reaction("👍")

    await asyncio.sleep(wait_time)

    message = await ctx.fetch_message(message.id)
    users = []

    # Para cada usuário que reagir, se diferente do BOT, adicionar na lista
    async for user in message.reactions[0].users():
        if user != bot.user:
            users.append(user)

    # Se houver mais de dois usuários
    if len(users) < 2:
        await ctx.send("❌❌ Poucos usuários reagiram. Tente novamente.")
        return

    # Randomizando e dividindo as equipes
    random.shuffle(users)
    team1 = users[:len(users)//2]
    team2 = users[len(users)//2:]

    team1_names = "\n".join([f"{i+1}. {user.name}" for i, user in enumerate(team1)])
    team2_names = "\n".join([f"{i+1}. {user.name}" for i, user in enumerate(team2)])

    # Configurando o Embed
    embed_reply = discord.Embed(
        title="⚪ Times",
        description=f"Times\nAleatorizados\n",
        color=0x00b0f4
    )

    img_embed_split = discord.File('imgs/ligadaslendas.jpg', 'ligadaslendas.jpg')
    embed_reply.set_image(url='attachment://ligadaslendas.jpg')

    thum_embed_split = discord.File('imgs/ligadaslendas.jpg', 'ligadaslendas.jpg')
    embed_reply.set_thumbnail(url='attachment://ligadaslendas.jpg')

    icon_author = discord.File('imgs/icon.jpg', 'icon.jpg')
    embed_reply.set_author(name="Marocos BOT", icon_url="attachment://icon.jpg")

    embed_reply.set_footer(text="Discord")

    embed_reply.add_field(name="\n📌 Team 1",
                value=f"{team1_names}",
                inline=False)

    embed_reply.add_field(name="\n📌 Team 2",
                value=f"{team2_names}",
                inline=False)

    message = await ctx.send(files=[thum_embed_split, icon_author], embed=embed_reply)

# Função para ver se o Player está ou não em partida, junto com alguns dados dela
@bot.command()
async def ingame(ctx, *, nametag=' '):
    usuario_dados = bf.data_perfil(nametag)
    
    if usuario_dados == 0:
        await ctx.reply(f'{nametag} não foi encontrado!')
        return
    
    ingame_api_link = f'https://br1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{usuario_dados[6]}?api_key={TOKEN_Riot}'
    ingame_response = requests.get(ingame_api_link)
    
    if ingame_response.status_code == 200:
        ingame_dados = ingame_response.json()

        # Calculando tempo de partida
        ingame_start_time = ingame_dados['gameStartTime']
        ingame_time = int(datetime.datetime.now().timestamp() * 1000)
        ingame_duration_time = (ingame_time - ingame_start_time)/1000
        inminutes, inseconds = divmod(ingame_duration_time, 60)

        ingame_type = ingame_dados['gameType']
        ingame_mode = ingame_dados['gameMode']

        if ingame_mode == 'CLASSIC':
            ingame_mode = "Summoner's Rift"

        if ingame_type == 'CUSTOM':
            ingame_type = "Personalizada"

        for every in ingame_dados['participants']:
            if every['puuid'] == usuario_dados[6]:
                ingame_champ = every['championId']
                ingame_champ = bf.champions_dict[ingame_champ]

        # Configurando o Embed
        embed_ingame = discord.Embed(title=usuario_dados[4], description="Partida em Andamento: ", color=0xFFD500)

        icon_author = discord.File('imgs/icon.jpg', 'icon.jpg')
        embed_ingame.set_author(name="Marocos BOT", icon_url="attachment://icon.jpg")

        icon = f"http://ddragon.leagueoflegends.com/cdn/14.13.1/img/profileicon/{usuario_dados[2]}.png"
        embed_ingame.set_thumbnail(url=icon)

        embed_ingame.add_field(name='Modo de Jogo:', value=f'{ingame_mode} ({ingame_type})', inline=False)
        embed_ingame.add_field(name='Campeão Selecionado: ', value=ingame_champ, inline=False)
        embed_ingame.add_field(name='Duração: ', value=f'{int(round(inminutes,0))} minutos e {int(round(inseconds, 0))} segundos', inline=False)

        message = await ctx.reply(file=icon_author, embed=embed_ingame)
    
    else: 
        message = await ctx.reply(f'{usuario_dados[4]} não está em Partida')

# Função Para fornecer alguns dados do perfil do Player
@bot.command()
async def perfil(ctx, *, nametag=' '):
    usuario_dados = bf.data_perfil(nametag)

    if usuario_dados == 0:
        await ctx.reply(f'{nametag} não foi encontrado!')
        return

    # Pegando os dados de maestria
    champ_dados = bf.data_mastery(nametag)
    # Pegando os dados de ranks
    ranks = bf.data_ranks(nametag)

    # Configurando o Embed
    embed_perfil = discord.Embed(title=usuario_dados[4], description=f"{usuario_dados[4]}#{usuario_dados[5]}\nNível: {usuario_dados[3]}", color=0xFFD500)

    icon_author = discord.File('imgs/icon.jpg', 'icon.jpg')
    embed_perfil.set_author(name="Marocos BOT", icon_url="attachment://icon.jpg")

    icon = f"http://ddragon.leagueoflegends.com/cdn/14.13.1/img/profileicon/{usuario_dados[2]}.png"
    embed_perfil.set_thumbnail(url=icon)

    embed_perfil.add_field(name='Maestrias',
                           value=f'{champ_dados[0][0]} com {champ_dados[0][1]} pontos\n{champ_dados[1][0]} com {champ_dados[1][1]} pontos\n{champ_dados[2][0]} com {champ_dados[2][1]} pontos', inline=False)
    
    # Comparações para determinar cada tipo de ranked
    if len(ranks[0]) > 1:
        if len(ranks[1]) > 1:
            embed_perfil.add_field(name="Ranked Solo-Duo", value=f'{ranks[0][0]} {ranks[0][1]}\nVitórias: {ranks[0][3]}\nDerrotas: {ranks[0][4]}\nPDL: {ranks[0][2]}', inline=False)
            embed_perfil.add_field(name="Ranked Flex", value=f'{ranks[1][0]} {ranks[1][1]}\nVitórias: {ranks[1][3]}\nDerrotas: {ranks[1][4]}\nPDL: {ranks[1][2]}')
        else:
            embed_perfil.add_field(name="Ranked Solo-Duo", value=f'{ranks[0][0]} {ranks[0][1]}\nVitórias: {ranks[0][3]}\nDerrotas: {ranks[0][4]}\nPDL: {ranks[0][2]}', inline=False)
            embed_perfil.add_field(name="Ranked Flex", value=f'Sem Ranqueamento', inline=False)
    
    else:
        if len(ranks[1]) > 1:
            embed_perfil.add_field(name="Ranked Solo-Duo", value=f'Sem Ranqueamento', inline=False)
            embed_perfil.add_field(name="Ranked Flex", value=f'{ranks[0][0]} {ranks[0][1]}\nVitórias: {ranks[0][3]}\nDerrotas: {ranks[0][4]}\nPDL: {ranks[0][2]}', inline=False)
        else:
            embed_perfil.add_field(name="Ranked Solo-Duo", value=f'Sem Ranqueamento', inline=False)
            embed_perfil.add_field(name="Ranked Flex", value=f'Sem Ranqueamento', inline=False)

    message = await ctx.reply(file=icon_author, embed=embed_perfil)

# Comando para pegar e apresentar as informações do último game do usuário
@bot.command()
async def lastgame(ctx, *, nametag=' '):
    usuario_dados = bf.data_perfil(nametag)

    if usuario_dados == 0:
        await ctx.reply(f'{nametag} não foi encontrado!')
        return

    # Carregando o ID da última partida
    matchid_api_link = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{usuario_dados[6]}/ids?start=0&count=20&api_key={TOKEN_Riot}'
    matchid_response = requests.get(matchid_api_link)
    matchid_dados = matchid_response.json()

    # Pegando os dados da última partida
    info_game = bf.data_game(matchid_dados[0], usuario_dados[0])

    # Determinando texto apresentativo do embeed
    if info_game[8] == 1:
        info_victory = '✅ Vitória!'
    else:
        info_victory = '❌ Derrota!'
    
    # Configurando o Embed
    embed_match = discord.Embed(title=usuario_dados[4], description=f"{info_victory}\n{info_game[0]} ({info_game[1]})\n", color=0xFFD500)

    icon_author = discord.File('imgs/icon.jpg', 'icon.jpg')
    embed_match.set_author(name="Marocos BOT", icon_url="attachment://icon.jpg")

    icon = f"http://ddragon.leagueoflegends.com/cdn/14.13.1/img/profileicon/{usuario_dados[2]}.png"
    embed_match.set_thumbnail(url=icon)

    embed_match.add_field(name='Campeão Selecionado: ', value=info_game[2], inline=False)
    embed_match.add_field(name='KDA', value=f'{info_game[4]}/{info_game[5]}/{info_game[6]}')
    embed_match.add_field(name='Duração: ', value=f'{int(round(info_game[6],0))} minutos e {int(round(info_game[7], 0))} segundos', inline=False)
    
    message = await ctx.reply(file=icon_author, embed=embed_match)            

# Comando para adicionar os dados da última partida (Não personalizada)
# Não será usada
@bot.command()
async def pontuar(ctx, *, nametag=' '):
    usuario_dados = bf.data_perfil(nametag)

    if usuario_dados == 0:
        await ctx.reply(f'{nametag} não foi encontrado!')
        return
    
    bf.pontuations_integrer(nametag)
    await ctx.reply('Pontuação adcionada com sucesso.')

# Comando para pontuar a ultima PERSONALIZADA 
@bot.command()
async def pontuar_ultima(ctx):
    try:
        result = subprocess.run(['python', 'C:\\Users\\marco\\Documents\\Pessoal\\Projetos_cod\\Marocos_BOT\\lcu.py'], check=True, capture_output=True)
        saida = result.stdout.splitlines() # Saídas do arquivo "lcu.py" rodado como subprocesso

        # Comparações para determianr a resposta do bot
        for x in saida:
            if "b'Essa partida ja foi contabilizada no banco de dados'" == str(x):
                await ctx.reply(f'A última partida personalizada já havia sido contabilizada!')
                return 0
            
            elif "b'O último jogo não foi uma personalizada.'"  == str(x):
                await ctx.reply(f'A última partida não foi uma personalizada!')
                return 0
    
        await ctx.reply(f'Pontuação contabilizada com sucesso!')

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar: {e}")
        await ctx.reply(f"Erro ao executar: {e}")

@bot.command()
async def ajuda(ctx):
    embed_help = discord.Embed(title='✅ Comandos diposníveis', description='Préfixo: "."', color=0xFFD500)

    icon_author = discord.File('imgs/icon.jpg', 'icon.jpg')
    embed_help.set_author(name="Marocos BOT", icon_url="attachment://icon.jpg")

    embed_help.add_field(name='dividir', value='Comando que dividirá as reações da mensagem em duas equipes', inline=False)
    embed_help.add_field(name='ingame *_nametag league of legends_', value='Comando para ver se o Player está em partida', inline=False)
    embed_help.add_field(name='perfil *_nametag league of legends_', value='Comando para ver ranks e maestrias do Player', inline=False)
    embed_help.add_field(name='lastgame *_nametag league of legends_', value='Comando com informações do último jogo do Player', inline=False)


    message = await ctx.reply(file=icon_author, embed=embed_help)  


bot.run(TOKEN_Discord)
