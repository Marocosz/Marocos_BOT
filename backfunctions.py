import requests
import csv

TOKEN_Riot = ""

# Definindo o Banco de Dados que liga o Campeão ao seu ID
champ_api_link = 'https://ddragon.leagueoflegends.com/cdn/14.13.1/data/en_US/champion.json'
champ_response = requests.get(champ_api_link)
champ_dados = champ_response.json()
champs = champ_dados['data']

# Gerando um dicionário com as informação - Campeão:ID
champions_dict = {int(details['key']): name for name, details in champs.items()}


# Função para tirar os 'espaços' dos nicks
def space(nametag):
    if nametag != ' ':
        if '#' in nametag:
            name, tag = nametag.split("#", 1)
            return name.replace(" ", "")+'#'+tag
        
        else:
            return ' '

    else:
        return ' '

# Função para formatar número de 123456 para 123.456
def format_number(numero):
    numb_str = str(numero)[::-1]
    parts = [numb_str[i:i+3] for i in range(0, len(numb_str), 3)]
    formated_number = '.'.join(parts)[::-1]

    return formated_number

# Função de leitura de CSV
def reader_csv(arq_name):
    with open(arq_name, mode='r', newline='', encoding='utf-8') as arq:
        csvreader = csv.reader(arq)
        data = list(csvreader)

    return data

# Função para escrever num CSV
def writer_csv(arq_name, data):
    with open(arq_name, mode='a', newline='', encoding='utf-8') as arquivo_csv:
        csvwriter = csv.writer(arquivo_csv)
        csvwriter.writerows(data)

# Função para pegar os devidos dados diante o nickname do usuário
def data_perfil(nametag):
    nametag = space(nametag)
    if '#' in nametag:
        name, tag = nametag.split("#", 1)
    else:
        return 0

    # Definindo o banco de dados inicial
    initial_api_link = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={TOKEN_Riot}"
    initial_response = requests.get(initial_api_link)

    if initial_response.status_code == 200:
        initial_dados = initial_response.json()
        PUUID = initial_dados['puuid']
        print(PUUID)

        # Definindo o banco de dados das informações da conta do usuário
        puuid_api_link = f"https://br1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{PUUID}?api_key={TOKEN_Riot}"
        puuid_response = requests.get(puuid_api_link)
        puuid_data = puuid_response.json()
        print(PUUID)

        # Definindo os itens importantes
        summoner_id = puuid_data['id']
        account_id = puuid_data['accountId']
        profile_icon_id = puuid_data['profileIconId']
        summoner_lvl = puuid_data['summonerLevel']
        gamename = initial_dados['gameName']
        tagline = initial_dados['tagLine']

        return [summoner_id, account_id, profile_icon_id, summoner_lvl, gamename, tagline, PUUID]

    else:
        return 0

# Função para pegar os devidos dados de maestria do usuário
def data_mastery(nametag):
    user_data = data_perfil(nametag)

    # Definindo o banco de dados de maestrias do usuário pelo PUUID
    mastery_api_link =f'https://br1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{user_data[6]}?api_key={TOKEN_Riot}'
    mastery_response = requests.get(mastery_api_link)
    mastery_dados = mastery_response.json()

    # Pegando os dados dos top 3 campeões do usuário
    champ1_dados = [champions_dict[mastery_dados[0]['championId']],mastery_dados[0]['championLevel'],
                    format_number(mastery_dados[0]['championPoints'])]
    
    champ2_dados = [champions_dict[mastery_dados[1]['championId']],mastery_dados[1]['championLevel'],
                    format_number(mastery_dados[1]['championPoints'])]
    
    champ3_dados = [champions_dict[mastery_dados[2]['championId']],mastery_dados[2]['championLevel'],
                    format_number(mastery_dados[2]['championPoints'])]

    return [champ1_dados, champ2_dados, champ3_dados]


def data_ranks(nametag):
    user_data = data_perfil(nametag)

    ranks_api_link = f"https://br1.api.riotgames.com/lol/league/v4/entries/by-summoner/{user_data[0]}?api_key={TOKEN_Riot}"
    ranks_response = requests.get(ranks_api_link)
    ranks_data = ranks_response.json()

    cherry = None
    solo = None
    flex = None

    # Tier, Rank, PDL, Vitórias, Derrotas
    if len(ranks_data) >= 1:
        for x in range(len(ranks_data)):
            if ranks_data[x]['queueType'] == 'CHERRY':
                cherry = x
            if ranks_data[x]['queueType'] == 'RANKED_SOLO_5x5':
                solo = x
            if ranks_data[x]['queueType'] == 'RANKED_FLEX_SR':
                flex = x

    if solo != None:
        data_soloduo = [ranks_data[solo]['tier'], ranks_data[solo]['rank'], ranks_data[solo]['leaguePoints'], ranks_data[solo]['wins'], ranks_data[solo]['losses']]
    else:
        data_soloduo = []
    
    if flex != None:
        data_flex = [ranks_data[flex]['tier'], ranks_data[flex]['rank'], ranks_data[flex]['leaguePoints'], ranks_data[flex]['wins'], ranks_data[flex]['losses']]
    else:
        data_flex = []
    
    return [data_soloduo, data_flex]

def data_game(gameid, summonerid):
    match_api_link = f'https://americas.api.riotgames.com/lol/match/v5/matches/{gameid}?api_key={TOKEN_Riot}'
    match_response = requests.get(match_api_link)
    match_dados = match_response.json()

    match_duration = match_dados['info']['gameDuration']
    minutes, seconds = divmod(match_duration, 60)

    match_mode = match_dados['info']['gameMode']
    match_type = match_dados['info']['gameType']

    participants = match_dados['info']['participants']
    

    for x in participants:
        if x['summonerId'] == summonerid:
            nickname = x['riotIdGameName']+'#'+x['riotIdTagline']
            match_champ = champions_dict[x['championId']]
            match_kills = x['kills']
            match_deaths = x['deaths']
            match_assists = x['assists']
            match_vitoria = 1 if x['win'] == True else 0
            match_loss = 1 if x['win'] == False else 0

    return [match_mode, match_type, match_champ, nickname,match_kills, match_deaths, match_assists, minutes, seconds, match_vitoria, match_loss]

def data_pontuations(nametag):
    user_data = data_perfil(nametag)

    matchid_api_link = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{user_data[6]}/ids?start=0&count=20&api_key={TOKEN_Riot}'
    matchid_response = requests.get(matchid_api_link)
    matchid_dados = matchid_response.json()

    gameid = matchid_dados[0]

    match_api_link = f'https://americas.api.riotgames.com/lol/match/v5/matches/{gameid}?api_key={TOKEN_Riot}'
    match_response = requests.get(match_api_link)
    match_dados = match_response.json()
    
    participants = match_dados['info']['participants']

    pontuations_dados = []
    for x in range(len(participants)):
        pontuations_dados.append(data_game(matchid_dados[0], participants[x]['summonerId']))
        pontuations_dados[x].pop(0)
        pontuations_dados[x].pop(0)
        pontuations_dados[x].pop(0)
        pontuations_dados[x].pop(4)
        pontuations_dados[x].pop(4)
    
    pontuations_dados.append(gameid)

    return pontuations_dados

def pontuations_integrer(data_match):
    data_pont = reader_csv('pontuations.csv')
    data_matches = reader_csv('matchesid.csv')
    
    header = ['Player', 'Kills', 'Deaths', 'Assists', 'Victorys', 'Losses']
    
    for id in data_matches:
        if int(id[0]) == int(data_match[-1]):
            
            print('Score dessa partida ja foi adicionado!')
            return 0
    
    writer_csv('matchesid.csv', [[data_match[-1]]])
    data_match.pop(-1)
    
    if not data_pont:
        with open('pontuations.csv', 'a+', newline='', encoding='utf-8') as arq:
            csvwriter = csv.writer(arq)
            csvwriter.writerow(header)
            csvwriter.writerows(data_match)
            
        print('Score adicionado com sucesso!')
        return 1
    
    else:    
        for item_match in data_match:
            nick_match = item_match[0]
            
            finded = False
            
            for item_pont in data_pont:
                nick_pont = item_pont[0]

                if nick_match == nick_pont:
                    for i in range(1, 6):
                        item_pont[i] = int(item_pont[i]) + int(item_match[i])       
                    finded = True
                    break
            
            if not finded:
                data_pont.append(item_match)
    
        # Limpando o conteúdo do csv
        with open('pontuations.csv', 'w') as arquivo:
            pass  # Não faz nada, apenas abre e fecha o arquivo, o que limpa seu conteúdo
        
        writer_csv('pontuations.csv', data_pont)
        
        print('Score adicionado com sucesso!')
        return 2
