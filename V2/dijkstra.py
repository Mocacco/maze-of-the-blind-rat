import requests
import asyncio
import websockets
import json
import heapq

API_URL = " https://3281-2804-14c-65a1-83de-cd0a-eaf6-8774-ecec.ngrok-free.app"

def criar_grupo(nome):
    payload = {"nome": nome}  
    response = requests.post(f"{API_URL}/grupo", json=payload)
    print("Corpo da resposta ao criar grupo:", response.text)

    if response.status_code == 200:
        try:
            return response.json()["GrupoId"]  
        except (ValueError, KeyError):
            print("Erro: A resposta não contém a chave 'GrupoId'.")
            return None
    else:
        print(f"Erro ao criar grupo: {response.status_code}, {response.text}")
        return None

def consultar_labirintos(grupo_id):
    if grupo_id:
        response = requests.get(f"{API_URL}/labirintos/{grupo_id}")
        print("Corpo da resposta ao consultar labirintos:", response.text)

        if response.status_code == 200:
            try:
                return response.json()["Labirintos"]
            except (ValueError, KeyError):
                print("Erro: A resposta não contém a chave 'Labirintos'.")
                return []
        else:
            print(f"Erro ao consultar labirintos: {response.status_code}, {response.text}")
            return []
    else:
        print("Grupo ID inválido")
        return []

def iniciar_desafio(grupo_id, labirinto_id):
    payload = {
        "grupo_id": grupo_id,
        "labirinto_id": labirinto_id
    }
    response = requests.post(f"{API_URL}/generate-websocket/", json=payload)
    print("Corpo da resposta ao iniciar desafio:", response.text)

    if response.status_code == 200:
        try:
            return response.json()["Conexao"]
        except (ValueError, KeyError):
            print("Erro: A resposta não contém a chave 'Conexao'.")
            return None
    else:
        print(f"Erro ao iniciar o desafio: {response.status_code}, {response.text}")
        return None

async def explorar_labirinto(websocket_url, entrada_id):
    distancias = {entrada_id: 0}  
    predecessores = {entrada_id: None}  
    vertices_a_explorar = [(0, entrada_id)] 
    visitados = set()  
    
    adjacencias = {}

    async with websockets.connect(websocket_url) as websocket:
        init_message = f"Ir:{entrada_id}"
        await websocket.send(init_message.encode('utf-8'))
        print(f"Iniciando exploração do labirinto... (Entrada: {entrada_id})")

        while True:
            response = await websocket.recv()
            data = json.loads(response)

            vertice_atual = data["Id"]
            adjacencias[vertice_atual] = data["Adjacencia"]

            print(f"Visitando vértice {vertice_atual} com adjacências: {data['Adjacencia']}")

            visitados.add(vertice_atual)

            if data["Tipo"] == 1:
                print(f"Saída encontrada no vértice {vertice_atual}!")
                caminho = []
                while vertice_atual is not None:
                    caminho.append(vertice_atual)
                    vertice_atual = predecessores.get(vertice_atual)
                print("Caminho para a saída:", caminho[::-1])  
                break

        
            for vizinho, custo in data["Adjacencia"]:
                if vizinho not in visitados:
                  
                    nova_distancia = distancias[vertice_atual] + 1  

                    if vizinho not in distancias or nova_distancia < distancias[vizinho]:
                        distancias[vizinho] = nova_distancia
                        predecessores[vizinho] = vertice_atual
                        heapq.heappush(vertices_a_explorar, (nova_distancia, vizinho))

            if not vertices_a_explorar:
                print("Não há mais vértices a explorar. Encerrando.")
                break

            _, proximo_vertice = heapq.heappop(vertices_a_explorar)
            move_message = f"Ir:{proximo_vertice}"
            await websocket.send(move_message.encode('utf-8'))
            print(f"Movendo-se para o vértice {proximo_vertice}")

if __name__ == "__main__":
    nome_grupo = "Grupo Teste"

    grupo_id = criar_grupo(nome_grupo)
    print(f"Grupo criado com ID: {grupo_id}")

    if grupo_id:
        labirintos = consultar_labirintos(grupo_id)
        print("Labirintos disponíveis:")
        for labirinto in labirintos:
            print(labirinto)

        if labirintos:
            labirinto_id = labirintos[0]["IdLabirinto"]
            websocket_url = iniciar_desafio(grupo_id, labirinto_id)
            print(f"WebSocket URL: {websocket_url}")

            if websocket_url:
                entrada_id = labirintos[0]["Entrada"]
                asyncio.run(explorar_labirinto(websocket_url, entrada_id))
        else:
            print("Nenhum labirinto disponível para explorar.")
    else:
        print("Falha ao criar grupo. Encerrando.")

