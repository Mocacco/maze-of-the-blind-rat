import requests
import asyncio
import websockets
import json

API_URL = "4ea7-2804-14c-65a1-83de-2c23-d166-bf14-1e34.ngrok-free.app"

# Função para criar um grupo
def criar_grupo(nome):
    payload = {"nome": nome}
    response = requests.post(f"http://{API_URL}/grupo", json=payload)
    print("Resposta ao criar grupo:", response.text)

    if response.status_code == 200:
        try:
            return response.json()["GrupoId"]
        except KeyError:
            print("Erro: A resposta não contém a chave 'GrupoId'.")
            return None
    else:
        print(f"Erro ao criar grupo: {response.status_code}, {response.text}")
        return None

# Função para listar todos os labirintos disponíveis
def listar_labirintos():
    print("Listando labirintos disponíveis...")
    response = requests.get(f"http://{API_URL}/labirintos")
    print("Resposta ao listar labirintos:", response.text)

    if response.status_code == 200:
        try:
            return response.json().get("labirintos", [])
        except KeyError:
            print("Erro: A resposta não contém a chave 'labirintos'.")
            return []
    else:
        print(f"Erro ao listar labirintos: {response.status_code}, {response.text}")
        return []

# Função para gerar WebSocket para o labirinto
def gerar_websocket(grupo_id, labirinto_id):
    payload = {
        "grupo_id": grupo_id,
        "labirinto_id": labirinto_id
    }
    response = requests.post(f"http://{API_URL}/generate-websocket", json=payload)
    print("Resposta ao gerar WebSocket:", response.text)

    if response.status_code == 200:
        try:
            return response.json()["websocket_url"]
        except KeyError:
            print("Erro: A resposta não contém a chave 'websocket_url'.")
            return None
    else:
        print(f"Erro ao gerar WebSocket: {response.status_code}, {response.text}")
        return None

# Função para explorar o labirinto via WebSocket
async def explorar_labirinto(websocket_url, entrada_id):
    async with websockets.connect(websocket_url) as websocket:
        init_message = f"ir:{entrada_id}"
        await websocket.send(init_message)
        print(f"Mensagem enviada para iniciar exploração: {init_message}")

        caminho = [entrada_id]
        while True:
            response = await websocket.recv()
            print("Resposta do WebSocket:", response)
            
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                print("Erro ao decodificar a resposta do WebSocket.")
                break

            vertice_atual = data.get("Id")
            adjacencias = data.get("Adjacencia", [])
            print(f"Visitando vértice {vertice_atual} com adjacências: {adjacencias}")

            if data.get("Tipo") == 2:  # Tipo 2 é "saida"
                print(f"Saída encontrada no vértice {vertice_atual}!")
                caminho.append(vertice_atual)
                break

            if adjacencias:
                proximo_vertice = adjacencias[0][0]
                move_message = f"ir:{proximo_vertice}"
                await websocket.send(move_message)
                print(f"Movendo-se para o vértice {proximo_vertice}")
                caminho.append(proximo_vertice)
            else:
                print("Não há mais vértices adjacentes. Encerrando.")
                break

        return caminho

# Função para finalizar o labirinto
def finalizar_labirinto(grupo_id, labirinto_id, caminho):
    payload = {
        "grupo": grupo_id,
        "labirinto": labirinto_id,
        "vertices": caminho
    }
    response = requests.post(f"http://{API_URL}/resposta", json=payload)
    print("Resposta ao finalizar labirinto:", response.text)

    if response.status_code == 200:
        print("Labirinto concluído com sucesso!")
    else:
        print(f"Erro ao finalizar labirinto: {response.status_code}, {response.text}")

# Fluxo principal
if __name__ == "__main__":
    nome_grupo = "MORFUGOLHO"
    
    # 1. Criar grupo
    grupo_id = criar_grupo(nome_grupo)
    print(f"Grupo criado com ID: {grupo_id}")

    if grupo_id:
        # 2. Listar todos os labirintos
        labirintos = listar_labirintos()
        print("Labirintos disponíveis:", labirintos)

        if labirintos:
            # Usar o primeiro labirinto disponível
            labirinto_id = labirintos[0]["labirinto"]
            print(f"Usando labirinto com ID: {labirinto_id}")

            # 3. Gerar WebSocket para explorar o labirinto
            websocket_url = gerar_websocket(grupo_id, labirinto_id)

            if websocket_url:
                entrada_id = 1  # Assumindo que o vértice de entrada tem ID 1
                print(f"Usando vértice de entrada com ID: {entrada_id}")
                caminho = asyncio.run(explorar_labirinto(websocket_url, entrada_id))
                
                if caminho and len(caminho) > 1:  # Verifica se o caminho foi encontrado e possui mais de um vértice
                    finalizar_labirinto(grupo_id, labirinto_id, caminho)
                else:
                    print("Falha ao explorar o labirinto. Caminho não encontrado.")
            else:
                print("Falha ao gerar WebSocket.")
        else:
            print("Nenhum labirinto disponível para explorar.")
    else:
        print("Falha ao criar grupo.")
