import requests

API_URL = "https://3281-2804-14c-65a1-83de-cd0a-eaf6-8774-ecec.ngrok-free.app"

def verificar_grupo(grupo_id):
    """Verificar se o grupo realmente existe antes de consultar labirintos."""
    response = requests.get(f"{API_URL}/grupo/{grupo_id}")
    print("Corpo da resposta ao verificar grupo:", response.text)
    
    if response.status_code == 200:
        print("Grupo encontrado.")
        return True
    else:
        print(f"Erro ao verificar grupo: {response.status_code}, {response.text}")
        return False

def consultar_labirintos(grupo_id):
    """Consultar os labirintos disponíveis para um grupo específico."""
    if grupo_id:
        print(f"Consultando labirintos para o grupo ID: {grupo_id}")
        response = requests.get(f"{API_URL}/labirintos/{grupo_id}")
        print("Corpo da resposta ao consultar labirintos:", response.text)

        if response.status_code == 200:
            try:
                return response.json()["Labirintos"]
            except (ValueError, KeyError):
                print("Erro: A resposta não contém a chave 'Labirintos'.")
                return []
        else:
            print(f"Erro ao consultar labirintos: {response.status_code}, {response.text}")
            return []
    else:
        print("Grupo ID inválido")
        return []

if __name__ == "__main__":
    grupo_id = "a8dbbc07bce54e968267d07d7c308366"

    # Verificar se o grupo existe antes de consultar labirintos
    if verificar_grupo(grupo_id):
        labirintos = consultar_labirintos(grupo_id)
        print("Labirintos disponíveis:")
        for labirinto in labirintos:
            print(labirinto)
    else:
        print("O grupo não foi encontrado.")
