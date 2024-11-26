import requests

API_URL = "0575-2804-14c-65a1-83de-cc56-fb52-f318-8412.ngrok-free.app"

def listar_labirintos():
    try:
        response = requests.get(f"http://{API_URL}/labirintos")

        if response.status_code == 200:
            try:
                labirintos = response.json()  
                if isinstance(labirintos, list):
                    print("Labirintos disponíveis:")
                    for labirinto in labirintos:
                        print(f"ID: {labirinto['id']}, Dificuldade: {labirinto['dificuldade']}")
                else:
                    print("Resposta:", labirintos)
            except ValueError as e:
                print("Erro ao decodificar JSON:", e)
                print("Resposta bruta:", response.text)
        else:
            print(f"Erro ao listar labirintos: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Erro ao fazer a requisição: {e}")

if __name__ == "__main__":
    listar_labirintos()