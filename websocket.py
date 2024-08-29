import asyncio
import websockets
import time

async def connect():
    uri = "ws://pornhub:8080"  
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("hora da punheta")
                await websocket.send("denovo pai?")
                
                async for message in websocket:
                    print(f"Mensagem do servidor: {message}")
        except (websockets.ConnectionClosedError, websockets.ConnectionClosedOK) as e:
            print(f"Conexão perdida: {e}. Tentando reconectar...")
            await asyncio.sleep(5)  # Espera 5 segundos antes de tentar reconectar
        except Exception as e:
            print(f"Erro: {e}")
            await asyncio.sleep(5)  # Espera 5 segundos antes de tentar reconectar

async def main():
    await connect()

if __name__ == "__main__":
    asyncio.run(main())
