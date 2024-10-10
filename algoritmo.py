import asyncio
import websockets
import json

# URL de conexão WebSocket (exemplo)
WEBSOCKET_URL = "ws://link.pro.handshake.inicial/"

# 1. onectar ao WebSocket e explorar o labirinto
async def explorar_labirinto():
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        print("Conectado ao WebSocket")

        # Resposta inicial com os dados do labirinto
        response = await websocket.recv()
        labirinto_info = json.loads(response)
        print(f"Dados do labirinto recebidos: {labirinto_info}")

        # Pegamos o vértice de entrada
        vertice_atual = labirinto_info.get('Entrada')
        labirinto_id = labirinto_info.get('LabirintoId')
        caminho = [vertice_atual]
        
        while True:
            print(f"Vértice atual: {vertice_atual}")

            # Comando para ir para um vértice vizinho
            ir_comando = {
                "Evento": "Ir",
                "VerticeId": vertice_atual
            }

            await websocket.send(json.dumps(ir_comando))
            response = await websocket.recv()
            dados_vertice = json.loads(response)
            
            adjacencia = dados_vertice.get("Adjacencia", [])
            tipo = dados_vertice.get("Tipo")

            # Se o vértice for uma saída
            if tipo == 1:
                print(f"Saída encontrada no vértice: {vertice_atual}")
                caminho.append(vertice_atual)
                break

            # Escolhe o próximo vértice de forma simples (o primeiro da adjacência)
            if adjacencia:
                vertice_atual = adjacencia[0]
                caminho.append(vertice_atual)
            else:
                print("Sem mais vértices para explorar.")
                break

        print("Caminho percorrido:", caminho)

# Função principal para executar a exploração
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(explorar_labirinto())
