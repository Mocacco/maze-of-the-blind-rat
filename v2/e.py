import requests
import websockets
import asyncio
import json
import re

API_URL = "254f-186-251-61-230.ngrok-free.app"

def listar_labirintos():
    try:
        response = requests.get(f"http://{API_URL}:8000/labirintos")
        if response.status_code == 200:
            labirintos = response.json()
            if isinstance(labirintos, list):
                print("Labirintos disponíveis:")
                for labirinto in labirintos:
                    print(f"ID: {labirinto['id']}, Dificuldade: {labirinto['dificuldade']}")
                while True:
                    id_labirinto = input("\nDigite o ID do labirinto desejado (ou 'sair' para cancelar): ").strip()
                    if id_labirinto.lower() == "sair":
                        print("Operação cancelada.")
                        return None
                    if any(str(l['id']) == id_labirinto for l in labirintos):
                        print(f"Labirinto selecionado: {id_labirinto}")
                        return id_labirinto
                    print("ID inválido. Por favor, insira um ID válido.")
            else:
                print("Estrutura inesperada na resposta:", labirintos)
        else:
            print(f"Erro ao listar labirintos: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Erro ao fazer a requisição: {e}")
        return None

def listar_grupos():
    try:
        response = requests.get(f"http://{API_URL}/grupos")
        if response.status_code == 200:
            grupos = response.json()
            if "Grupos" in grupos and isinstance(grupos["Grupos"], list):
                print("Grupos disponíveis:")
                for grupo in grupos["Grupos"]:
                    print(f"ID: {grupo['id']}, Nome: {grupo['nome']}, Labirintos Concluídos: {grupo['labirintos_concluidos']}")
                return grupos["Grupos"]
            else:
                print("Estrutura inesperada na resposta:", grupos)
        else:
            print(f"Erro ao listar grupos: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Erro ao fazer a requisição: {e}")



async def explorar_labirinto(websocket_url):
    """
    Exploração do labirinto usando WebSocket.
    """
    print(f"Conectando ao WebSocket: {websocket_url}")
    percurso = []  # Lista para armazenar o percurso (vértices visitados)

    try:
        async with websockets.connect(websocket_url) as websocket:
            print("Conexão estabelecida. Iniciando exploração...")

            while True:
                response = await websocket.recv()
                print(f"Resposta do servidor: {response}")

                # Verifica se a resposta está no formato esperado
                try:
                    # A resposta tem a estrutura 'Vértice atual: {valor}, Tipo: {valor}, Adjacentes(Vertice, Peso): [{lista}]'
                    match = re.search(
                        r"Vértice atual: (\d+), Tipo: (\d+), Adjacentes\(Vertice, Peso\): \[(.*)\]",
                        response
                    )

                    if match:
                        vertice_atual = int(match.group(1))  # Extraímos o vértice atual
                        tipo = int(match.group(2))  # Extraímos o tipo
                        adjacentes_str = match.group(3)  # Extraímos a lista de adjacentes como string
                        
                        # Convertendo a string de adjacentes para uma lista de tuplas
                        adjacentes = []
                        for item in adjacentes_str.split("),"):
                            adj = item.strip().replace("(", "").replace(")", "")
                            if adj:
                                vert, peso = map(int, adj.split(","))
                                adjacentes.append((vert, peso))

                        print(f"Vértice atual: {vertice_atual}, Tipo: {tipo}")
                        print(f"Vértices adjacentes: {adjacentes}")

                        percurso.append(vertice_atual)

                        # Envia o JSON para o servidor com as informações
                    

                        # Se tipo for "saída", encerra a exploração
                        if tipo == 2:  # Assumindo que '2' indica saída
                            print(f"Saída encontrada no vértice {vertice_atual}!")
                            break

                        # Move para o próximo vértice
                        if adjacentes:
                            proximo_vertice = adjacentes[0][0]
                            comando_movimento = f"ir:{proximo_vertice}"  # Comando correto para se mover
                            await websocket.send(comando_movimento)  # Envia o comando no formato correto
                            print(f"Movendo-se para o vértice {proximo_vertice}")
                        else:
                            print("Sem vértices adjacentes. Exploração encerrada.")
                            break
                    else:
                        print("Erro ao interpretar a resposta do servidor: formato inesperado.")
                        break

                except Exception as e:
                    print(f"Erro ao interpretar mensagem do servidor: {e}")
                    break

            return percurso
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Conexão fechada: {e}. Tentando reconectar...")
        await asyncio.sleep(2)
    except Exception as e:
        print(f"Erro inesperado: {e}")
    return percurso

def gerar_link_websocket(grupo_id, labirinto_id):
    try:
        response = requests.post(
            f"http://{API_URL}/generate-websocket",
            json={"grupo_id": grupo_id, "labirinto_id": labirinto_id},
        )
        if response.status_code == 200:
            data = response.json()
            websocket_url = data.get("websocket_url")
            if websocket_url:
                print(f"WebSocket URL gerado: {websocket_url}")
                return websocket_url
            else:
                print("Erro: URL do WebSocket não encontrada na resposta.")
        else:
            print(f"Erro ao gerar o WebSocket: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")
    return None

def finalizar_labirinto(grupo_id, labirinto_id, percurso):
    try:
        # Ajuste para enviar os dados conforme a documentação
        dados_finalizacao = {
            "grupo": grupo_id,  # UUID do grupo
            "labirinto": int(labirinto_id),  # ID do labirinto (deve ser um inteiro)
            "vertices": percurso,  # Lista de vértices no percurso
        }

        # Envia a requisição para finalizar o labirinto
        response = requests.post(
            f"http://{API_URL}/resposta",
            json=dados_finalizacao,
        )

        if response.status_code == 200:
            data = response.json()
            print(f"Resposta do servidor: {data.get('message')}")
        else:
            print(f"Erro ao finalizar o labirinto: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")




if __name__ == "__main__":
    print("Listando labirintos...")
    listar_labirintos()
    print("\nListando grupos...")
    listar_grupos()
    grupo_id = input("Digite o ID do grupo: ").strip()
    labirinto_id = input("Digite o ID do labirinto: ").strip()

    print("\nGerando link WebSocket...")
    websocket_url = gerar_link_websocket(grupo_id, labirinto_id)

    if labirinto_id:
        websocket_url = gerar_link_websocket(grupo_id, labirinto_id)
        if websocket_url:
            # Alterado para compatível com loop já em execução (caso esteja em Jupyter ou outro ambiente)
            if asyncio.get_event_loop().is_running():
                asyncio.ensure_future(explorar_labirinto(websocket_url))
            else:
                percurso = asyncio.run(explorar_labirinto(websocket_url))
            if percurso:
                finalizar_labirinto(grupo_id, labirinto_id, percurso)
