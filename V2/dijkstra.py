import requests
import asyncio
import websockets
import json

API_URL = "0575-2804-14c-65a1-83de-cc56-fb52-f318-8412.ngrok-free.app"

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

def criar_labirinto(dificuldade, vertices, arestas):
    payload = {
        "dificuldade": dificuldade,
        "vertices": vertices,
        "arestas": arestas
    }
    response = requests.post(f"http://{API_URL}/labirinto", json=payload)
    print("Resposta ao criar labirinto:", response.text)

    if response.status_code == 200:
        try:
            return response.json()["LabirintoId"]
        except KeyError:
            print("Erro: A resposta não contém a chave 'LabirintoId'.")
            return None
    else:
        print(f"Erro ao criar labirinto: {response.status_code}, {response.text}")
        return None

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

async def explorar_labirinto(websocket_url, entrada_id):
    async with websockets.connect(websocket_url) as websocket:
        init_message = f"ir:{entrada_id}"
        await websocket.send(init_message)
        print(f"Mensagem enviada para iniciar exploração: {init_message}")

        caminho = [entrada_id]
        while True:
            response = await websocket.recv()
            print("Resposta do WebSocket:", response)

            if "Vértice atual:" in response:
                parts = response.split(", ")
                vertice_atual = int(parts[0].split(": ")[1])
                adjacentes = eval(parts[-1].split(": ")[1]) 
                print(f"Visitando vértice {vertice_atual} com adjacências: {adjacentes}")

                if "Tipo: saida" in response:
                    print(f"Saída encontrada no vértice {vertice_atual}!")
                    caminho.append(vertice_atual)
                    break

                if adjacentes:
                    proximo_vertice = adjacentes[0][0]
                    move_message = f"ir:{proximo_vertice}"
                    await websocket.send(move_message)
                    print(f"Movendo-se para o vértice {proximo_vertice}")
                    caminho.append(proximo_vertice)
                else:
                    print("Não há mais vértices adjacentes. Encerrando.")
                    break
            else:
                print("Resposta inesperada do WebSocket:", response)
                break

        return caminho

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

if __name__ == "__main__":
    nome_grupo = "TESTE"
    
    grupo_id = criar_grupo(nome_grupo)
    print(f"Grupo criado com ID: {grupo_id}")

    if grupo_id:
        vertices = [{"id": 1, "tipo": 0}, {"id": 2, "tipo": 1}]  
        arestas = [{"origemId": 1, "destinoId": 2, "peso": 1}]
        labirinto_id = criar_labirinto("basiquinho", vertices, arestas)

        if labirinto_id:
            labirintos = listar_labirintos()
            print("Labirintos disponíveis:", labirintos)
            websocket_url = gerar_websocket(grupo_id, labirinto_id)
            if websocket_url:
                entrada_id = vertices[0]["id"]
                print(f"Usando vértice de entrada com ID: {entrada_id}")
                caminho = asyncio.run(explorar_labirinto(websocket_url, entrada_id))
                
                if caminho and len(caminho) > 1:  
                    finalizar_labirinto(grupo_id, labirinto_id, caminho)
                else:
                    print("Falha ao explorar o labirinto. Caminho não encontrado.")
            else:
                print("Falha ao gerar WebSocket.")
        else:
            print("Falha ao criar labirinto.")
    else:
        print("Falha ao criar grupo.")
