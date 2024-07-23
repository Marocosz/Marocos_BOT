import asyncio
from lcu_driver import Connector
import backfunctions as bf
import sys

connector = Connector()

geral_data = None

async def data_custom(connection):
    print('Client connected')
    data = []

    match_id = sys.argv[1]
    match_details_response = await connection.request('get', f'/lol-match-history/v1/games/{match_id}')

    if match_details_response.status == 200:
        match_details = await match_details_response.json()

        participants_id = match_details['participantIdentities']

            # Extrair KDA de cada jogador e adicioná-lo na lista
        for participant in match_details['participants']:
            for everyid in participants_id:
                if everyid['participantId'] == participant['participantId']:
                    summoner_name = everyid['player']['gameName']
                    stats = participant['stats']
                    kills = stats['kills']
                    deaths = stats['deaths']
                    assists = stats['assists']
                    win = 1 if stats['win'] == True else 0
                    loss = 1 if stats['win'] == False else 0

            data.append([summoner_name, kills, deaths, assists, win, loss])
                            
    else:
        print(f"Failed to retrieve match details. Status code: {match_details_response.status}")
        return 2

    # Fechar a conexão após a solicitação
    await connector.stop()

    # Adicionando o ID da partida para aderir ao sistema de integrer
    data.append(match_id)
    return data

@connector.close
async def disconnect(_):
    print('Client disconnected')

# Rodando o data_custom ao iniciar o connector
@connector.ready
async def start(_):
    global geral_data
    geral_data = await data_custom(connector.connection)

connector.start()

bf.pontuations_integrer(geral_data)

sys.exit() # Fechando o arquivo
