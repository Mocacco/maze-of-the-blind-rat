import requests
import asyncio
import websockets
import json
import heapq


API_URL = "https://26c2-2804-14c-65a1-83de-54b0-da06-be76-de9b.ngrok-free.app"
ARQUIVO_GRUPOS = "grupos.txt"  

def criar_grupo(nome):
    
    with open(ARQUIVO_GRUPOS, 'a') as arquivo:
        arquivo.write(f"{nome}\n")  

    response = requests.post(f"{API_URL}/grupo", json={"Nome": nome})

    print("Corpo da resposta:", response.text)  

    if response.status_code == 200:
        try:
            return response.json()["Id"]
        except ValueError:
            print("Erro ao decodificar JSON:", response.text)
            return None
    else:
        print(f"Erro: {response.status_code}, Mensagem: {response.text}")
        return None



def iniciar_desafio(grupo_id):
    response = requests.get(f"{API_URL}/iniciar/{grupo_id}")
    if response.status_code == 200:
        return response.json()["Conexao"]
    else:
        print(f"Erro ao iniciar o desafio: {response.status_code}, Mensagem: {response.text}")
        return None


def consultar_labirintos(grupo_id):
    response = requests.get(f"{API_URL}/labirintos/{grupo_id}")
    if response.status_code == 200:
        return response.json()["Labirintos"]
    else:
        print(f"Erro ao consultar labirintos: {response.status_code}, Mensagem: {response.text}")
        return []


def dijkstra(grafo, inicio, saida):
    fila_prioridade = []
    heapq.heappush(fila_prioridade, (0, inicio))
    distancias = {v: float('inf') for v in grafo}
    distancias[inicio] = 0
    caminho = {inicio: None}

    while fila_prioridade:
        distancia_atual, vertice_atual = heapq.heappop(fila_prioridade)

        if vertice_atual == saida:
            break  

        for vizinho, peso in grafo[vertice_atual].items():
            distancia = distancia_atual + peso

            if distancia < distancias[vizinho]:
                distancias[vizinho] = distancia
                caminho[vizinho] = vertice_atual
                heapq.heappush(fila_prioridade, (distancia, vizinho))

    return caminho, distancias


async def explorar_labirinto(websocket_url, entrada_id):
    async with websockets.connect(websocket_url) as websocket:
        
        init_message = f"Ir:{entrada_id}"
        await websocket.send(init_message.encode('utf-8'))
        print("Iniciando exploração do labirinto...")

        grafo = {}  

        while True:
            
            response = await websocket.recv()
            data = json.loads(response)

            
            vertice_atual = data["Id"]
            adjacencias = data["Adjacencia"]
            grafo[vertice_atual] = {adj: 1 for adj in adjacencias}  

            print(f"Visitando vértice {vertice_atual} com adjacências: {data['Adjacencia']}")

            
            if data["Tipo"] == 1:
                print(f"Saída encontrada no vértice {vertice_atual}!")
                saida = vertice_atual
                break

           
            for adj in adjacencias:
                if adj not in grafo:
                    grafo[adj] = {}

            
            if adjacencias:
                proximo_vertice = adjacencias[0]  
                move_message = f"Ir:{proximo_vertice}"
                await websocket.send(move_message.encode('utf-8'))
                print(f"Movendo-se para o vértice {proximo_vertice}")
            else:
                print("Não há vizinhos disponíveis. Encerrando a exploração.")
                break

        
        print("Aplicando Dijkstra...")
        caminho_dijkstra, distancias = dijkstra(grafo, entrada_id, saida)
        
        
        caminho = []
        vertice = saida
        while vertice is not None:
            caminho.append(vertice)
            vertice = caminho[vertice] if vertice in caminho else None
        caminho.reverse()  

        print("Caminho mais curto até a saída:", caminho)
        print("Distâncias a partir da entrada:", distancias)


if __name__ == "__main__":
    nome_grupo = "Grupo de Desafio"

    
    grupo_id = criar_grupo(nome_grupo)
    print(f"Grupo criado com ID: {grupo_id}")

    websocket_url = iniciar_desafio(grupo_id)
    print(f"WebSocket URL: {websocket_url}")

    labirintos = consultar_labirintos(grupo_id)
    print("Labirintos disponíveis:")
    for labirinto in labirintos:
        print(labirinto)

    if labirintos:
        entrada_id = labirintos[0]["Entrada"]
        asyncio.run(explorar_labirinto(websocket_url, entrada_id))
    else:
        print("Nenhum labirinto disponível para explorar.")
