import requests
import asyncio
import websockets
import json
import heapq

API_URL = " https://0c49-2804-14c-65a1-83de-3018-be30-c8ef-4162.ngrok-free.app" 

def criar_grupo(nome):
    payload = {"nome": nome}
    response = requests.post(f"{API_URL}/grupo", json=payload)
    print("Corpo da resposta:", response.text)  
    if response.status_code == 200:
        return response.json().get("GrupoId")  
    else:
        print(f"Erro ao criar grupo: {response.status_code}, {response.text}")
        return None

# Testando a função
nome_grupo = "Grupo de Desafio"
grupo_id = criar_grupo(nome_grupo)
print(f"Grupo criado com ID: {grupo_id}")

def iniciar_desafio(grupo_id, labirinto_id):
    payload = {"grupo_id": grupo_id, "labirinto_id": labirinto_id}
    response = requests.post(f"{API_URL}/generate-websocket/", json=payload)
    print("Corpo da resposta ao iniciar desafio:", response.text)
    if response.status_code == 200:
        return response.json().get("Conexao")
    else:
        print(f"Erro ao iniciar o desafio: {response.status_code}, {response.text}")
        return None

def consultar_labirintos(grupo_id):
    if grupo_id:
        response = requests.get(f"{API_URL}/labirintos/{grupo_id}")
        print("Corpo da resposta ao consultar labirintos:", response.text)  
        
        if response.status_code == 200:
            try:
                dados_resposta = response.json()
                if "Labirintos" in dados_resposta:
                    return dados_resposta["Labirintos"]
                else:
                    print("Erro: A chave 'Labirintos' não está presente na resposta.")
                    return []
            except ValueError:
                print("Erro ao tentar decodificar a resposta como JSON:", response.text)
                return []
        else:
            print(f"Erro ao consultar labirintos: {response.status_code}, Mensagem: {response.text}")
            return []
    else:
        print("Grupo ID inválido")
        return []

async def explorar_labirinto(websocket_url, entrada_id):
    async with websockets.connect(websocket_url) as websocket:
        init_message = f"Ir:{entrada_id}"
        await websocket.send(init_message.encode('utf-8'))
        print("Iniciando exploração do labirinto...")

        grafo = {}
        visitados = set()  
        pilha = [entrada_id]  

        while pilha:
            vertice_atual = pilha.pop()  
            if vertice_atual in visitados:
                continue  

            visitados.add(vertice_atual)  
            await websocket.send(f"Ir:{vertice_atual}".encode('utf-8'))
            print(f"Movendo-se para o vértice {vertice_atual}")

            response = await websocket.recv()
            data = json.loads(response)

            
            adjacencias = data.get("Adjacencia", [])
            grafo[vertice_atual] = {vizinho[0]: vizinho[1] for vizinho in adjacencias}
            print(f"Vértice {vertice_atual}, Adjacências: {adjacencias}")

            if data["Tipo"] == 1: 
                print(f"Saída encontrada no vértice {vertice_atual}!")
                break 

         
            for vizinho in adjacencias:
                if vizinho[0] not in visitados: 
                    pilha.append(vizinho[0])
                    print(f"Adicionando {vizinho[0]} à pilha para visitar depois.")
        
        print("Exploração finalizada.")

if __name__ == "__main__":
    nome_grupo = "Grupo de Desafio"
    grupo_id = criar_grupo(nome_grupo)
    print(f"Grupo criado com ID: {grupo_id}")

    if grupo_id:
        labirintos = consultar_labirintos(grupo_id)
        if labirintos:
            labirinto_id = labirintos[0]["IdLabirinto"]
            websocket_url = iniciar_desafio(grupo_id, labirinto_id)
            print(f"WebSocket URL: {websocket_url}")

            if websocket_url:
                entrada_id = labirintos[0]["Entrada"]
                asyncio.run(explorar_labirinto(websocket_url, entrada_id))
            else:
                print("Falha ao obter URL do WebSocket.")
        else:
            print("Nenhum labirinto disponível para explorar.")