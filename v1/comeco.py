import asyncio
import websockets
import json

websocket_url = "ws://bugalu/"


async def explore_maze():
    async with websockets.connect(websocket_url) as websocket:
        labirinto = {}
        visitados = set()  
        stack = []  

        init_message = {
            "GrupoId": "3F4365C5-77F1-405E-A6F2-66BE20521A40", 
            "LabirintoId": 0,  
            "Evento": "Ir", 
            "Entrada": 0 
        }
        await websocket.send(json.dumps(init_message))
        print("Iniciando exploração do labirinto...")

        while True:
            response = await websocket.recv()
            data = json.loads(response)
            vertice_atual = data["VerticeId"]

            labirinto[vertice_atual] = data["Adjacencia"]
            visitados.add(vertice_atual)
            print(f"Visitando vértice {vertice_atual} com adjacências: {data['Adjacencia']}")

            if data.get("Tipo") == 1:  
                print(f"Saída encontrada no vértice {vertice_atual}!")
                break

            for vizinho in data["Adjacencia"]:
                if vizinho not in visitados:
                    stack.append(vizinho)

            if stack:
                proximo_vertice = stack.pop()
                move_message = {
                    "Evento": "Ir",
                    "VerticeId": proximo_vertice
                }
                await websocket.send(json.dumps(move_message))
                print(f"Movendo-se para o vértice {proximo_vertice}")
            else:
                print("Exploração completa, sem mais vértices para visitar.")
                break

        caminho_curto = encontrar_melhor_caminho(labirinto, init_message["Entrada"], vertice_atual)
        print(f"Melhor caminho para a saída: {caminho_curto}")


def encontrar_melhor_caminho(labirinto, inicio, saida):
    from collections import deque
    fila = deque([[inicio]])
    visitados = set()

    while fila:
        caminho = fila.popleft()
        vertice = caminho[-1]

        if vertice == saida:
            return caminho

        if vertice not in visitados:
            visitados.add(vertice)
            for vizinho in labirinto[vertice]:
                novo_caminho = list(caminho)
                novo_caminho.append(vizinho)
                fila.append(novo_caminho)

    return None  

asyncio.get_event_loop().run_until_complete(explore_maze())
