import requests
import asyncio
import websockets
import json

API_URL = "http://localhost:8000"

def criar_labirinto_grande():
    payload = {
        "dificuldade": "grande",
        "vertices": [
            {"id": 1, "tipo": 1},  # Entrada
            {"id": 2, "tipo": 0},
            {"id": 3, "tipo": 0},
            {"id": 4, "tipo": 2},  # Saída
            # Adicione todos os vértices do labirinto grande...
        ],
        "arestas": [
            {"origemId": 1, "destinoId": 2, "peso": 1},
            {"origemId": 2, "destinoId": 3, "peso": 1},
            {"origemId": 3, "destinoId": 4, "peso": 1},
            # Adicione todas as arestas do labirinto grande...
        ]
    }

    response = requests.post(f"{API_URL}/labirinto", json=payload)
    if response.status_code == 200:
        labirinto_id = response.json().get("LabirintoId")
        print(f"Labirinto grande criado com sucesso! ID: {labirinto_id}")
        return labirinto_id
    else:
        print(f"Erro ao criar labirinto: {response.status_code}")
        print("Resposta:", response.text)
        return None

def gerar_websocket(grupo_id, labirinto_id):
    payload = {
        "grupo_id": grupo_id,
        "labirinto_id": labirinto_id
    }
    response = requests.post(f"{API_URL}/generate-websocket", json=payload)
    if response.status_code == 200:
        return response.json().get("websocket_url")
    else:
        print(f"Erro ao gerar WebSocket: {response.status_code}")
        return None

async def explorar_labirinto(websocket_url, entrada_id):
    caminho = []
    try:
        async with websockets.connect(websocket_url) as websocket:
            # Envia o comando para começar do vértice de entrada
            await websocket.send(f"ir:{entrada_id}")
            caminho.append(entrada_id)

            while True:
                response = await websocket.recv()
                data = json.loads(response)

                vertice_atual = data.get("Id")
                tipo = data.get("Tipo")
                adjacencias = data.get("Adjacencia", [])

                print(f"Visitando vértice {vertice_atual}. Tipo: {tipo}, Adjacências: {adjacencias}")

                # Verifica se encontrou a saída
                if tipo == 2:
                    print(f"Saída encontrada no vértice {vertice_atual}!")
                    caminho.append(vertice_atual)
                    break

                # Seleciona o próximo vértice (pode implementar lógica mais avançada aqui)
                if adjacencias:
                    proximo_vertice = adjacencias[0][0]
                    await websocket.send(f"ir:{proximo_vertice}")
                    caminho.append(proximo_vertice)
                else:
                    print("Nenhuma adjacência disponível. Labirinto incompleto.")
                    break

    except Exception as e:
        print(f"Erro durante a exploração do labirinto: {e}")
    return caminho

def finalizar_labirinto(grupo_id, labirinto_id, caminho):
    payload = {
        "grupo": grupo_id,
        "labirinto": labirinto_id,
        "vertices": caminho
    }
    response = requests.post(f"{API_URL}/resposta", json=payload)
    if response.status_code == 200:
        print("Labirinto concluído com sucesso!")
    else:
        print(f"Erro ao finalizar labirinto: {response.status_code}")
        print("Resposta da API:", response.text)

def executar_labirinto_grande():
    # Criar grupo
    grupo_payload = {"nome": "Grupo_Labirinto_Grande"}
    grupo_response = requests.post(f"{API_URL}/grupo", json=grupo_payload)
    grupo_id = grupo_response.json().get("GrupoId")

    if not grupo_id:
        print("Erro ao criar grupo.")
        return

    # Criar labirinto
    labirinto_id = criar_labirinto_grande()
    if not labirinto_id:
        print("Erro ao criar labirinto grande.")
        return

    # Gerar WebSocket
    websocket_url = gerar_websocket(grupo_id, labirinto_id)
    if not websocket_url:
        print("Erro ao gerar WebSocket.")
        return

    # Explorar o labirinto
    entrada_id = 1  # Supondo que o vértice 1 é a entrada
    caminho = asyncio.run(explorar_labirinto(websocket_url, entrada_id))

    if caminho:
        print("Caminho encontrado:", caminho)
        # Finalizar o labirinto
        finalizar_labirinto(grupo_id, labirinto_id, caminho)
    else:
        print("Falha ao explorar o labirinto. Nenhum caminho encontrado.")

if __name__ == "__main__":
    executar_labirinto_grande()