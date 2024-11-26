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
    try:
        response = requests.get(f"http://{API_URL}/labirintos")
        
        if response.status_code == 200:
            data = response.json()  
            labirintos = data.get('labirintos', [])  
            
            if labirintos:  
                print("Labirintos encontrados:")
                for labirinto in labirintos:
                    print(f"ID: {labirinto['labirinto']}, Dificuldade: {labirinto['dificuldade']}")
            else:
                print("Nenhum labirinto encontrado.")
            
            return labirintos
        else:
            print(f"Erro ao listar labirintos: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Erro ao fazer a requisição: {e}")

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


def listar_vertices_labirinto(labirinto_id):
    try:
        response = requests.get(f"http://{API_URL}/labirinto/{labirinto_id}/vertices")
        if response.status_code == 200:
            vertices = response.json()  
            print(f"Vértices do labirinto {labirinto_id}:")
            for vertice in vertices:
                print(f"ID: {vertice['id']}, Tipo: {vertice['tipo']}")
            return vertices
        else:
            print(f"Erro ao listar vértices: {response.status_code}, {response.text}")
            return []
    except Exception as e:
        print(f"Erro ao fazer a requisição: {e}")
        return []


async def explorar_labirinto(websocket_url, entrada_id):
    tentativas_maximas = 5  # Número máximo de tentativas
    tentativas = 0
    while tentativas < tentativas_maximas:
        try:
            async with websockets.connect(websocket_url) as websocket:
                init_message = f"ir:{entrada_id}"
                print(f"Mensagem enviada para iniciar exploração: {init_message}")
                await websocket.send(init_message)

                caminho = [entrada_id]
                while True:
                    response = await websocket.recv()
                    print(f"Resposta recebida do WebSocket: {response}")

                    if isinstance(response, str):  # Resposta em formato texto
                        print("Resposta em formato texto (txt). Processando como texto.")
                        if "Vértice de entrada não encontrado" in response:
                            print("Erro: Vértice de entrada não encontrado.")
                            # Tente usar outro ID de entrada, se possível
                            print("Tentando outro vértice de entrada...")
                            entrada_id = 1 # Altere para outro ID, se necessário
                            init_message = f"ir:{entrada_id}"
                            await websocket.send(init_message)
                            caminho = [entrada_id]  # Reinicia a exploração com o novo ID
                        elif "Saída encontrada" in response:
                            print("Saída encontrada no texto da resposta.")
                            break
                        else:
                            print("Resposta não processada corretamente.")
                            break
                    else:
                        try:
                            data = json.loads(response)
                            print("Resposta decodificada com sucesso:", data)
                            
                            vertice_atual = data.get("Id")
                            adjacencias = data.get("Adjacencia", [])
                            tipo = data.get("Tipo")
                            print(f"Visitando vértice {vertice_atual} com adjacências: {adjacencias}")

                            if tipo == 2:  # Tipo 2 é a saída
                                print(f"Saída encontrada no vértice {vertice_atual}!")
                                caminho.append(vertice_atual)
                                break

                            if adjacencias:
                                proximo_vertice = adjacencias[0][0]
                                move_message = f"ir:{proximo_vertice}"
                                print(f"Movendo-se para o vértice {proximo_vertice}")
                                await websocket.send(move_message)
                                caminho.append(proximo_vertice)
                            else:
                                print("Não há mais vértices adjacentes. Encerrando.")
                                break

                        except json.JSONDecodeError:
                            print("Erro ao decodificar a resposta do WebSocket. Resposta não é JSON e não é texto esperado.")
                            break

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Erro de conexão fechada: {e}. Tentando reconectar...")
            tentativas += 1
            await asyncio.sleep(2)  # Aguarda 2 segundos antes de tentar reconectar
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            break

    if tentativas == tentativas_maximas:
        print("Número máximo de tentativas atingido. Falha ao explorar o labirinto.")
    return caminho


if __name__ == "__main__":
    nome_grupo = "TESTE"
    grupo_id = criar_grupo(nome_grupo)
    print(f"Grupo criado com ID: {grupo_id}")

    if grupo_id:
        # Criar um labirinto grande
        vertices = [{"id": i, "tipo": 1} for i in range(1, 101)]  # 100 vértices
        vertices[-1]["tipo"] = 2  # Define o último vértice como a saída

        # Criar conexões entre os vértices
        arestas = []
        for i in range(1, 100):  # Conecta cada vértice ao próximo
            arestas.append({"origemId": i, "destinoId": i + 1, "peso": 1})

        # Conexões extras para maior complexidade
        for i in range(1, 50, 2):  # Conecta vértices alternados para formar caminhos adicionais
            if i + 10 <= 100:
                arestas.append({"origemId": i, "destinoId": i + 10, "peso": 2})

        labirinto_id = criar_labirinto("gigante", vertices, arestas)

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
            print("Não foi possível obter os vértices do labirinto.")
    else:
        print("Falha ao criar grupo.")