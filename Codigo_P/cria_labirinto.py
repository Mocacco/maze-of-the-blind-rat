import requests
import json

API_URL = "5b05-2804-14c-65a1-83de-2c25-1590-316a-4c70.ngrok-free.app"

def criar_labirinto(dificuldade, vertices, arestas):
    """
    Cria um novo labirinto com seus vértices e arestas.
    :param dificuldade: Nível de dificuldade do labirinto
    :param vertices: Lista de vértices com 'id' e 'tipo' (1 para entrada, 2 para saída)
    :param arestas: Lista de arestas com 'origemId', 'destinoId' e 'peso'
    :return: ID do labirinto criado ou None em caso de erro
    """
    dados_labirinto = {
        "dificuldade": dificuldade,
        "vertices": vertices,
        "arestas": arestas
    }

    try:
        response = requests.post(f"http://{API_URL}/labirinto", json=dados_labirinto)
        
        if response.status_code == 200:
            data = response.json()
            labirinto_id = data.get("LabirintoId")
            if labirinto_id:
                print(f"Labirinto criado com sucesso! ID: {labirinto_id}")
                return labirinto_id
            else:
                print("Erro: ID do labirinto não encontrado na resposta.")
        else:
            print(f"Erro ao criar labirinto: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    return None

# Exemplo de uso da função com dados simples
if __name__ == "__main__":
    dificuldade = "Fácil"
    vertices = [
        {"id": 1, "tipo": 1},  # Entrada
        {"id": 2, "tipo": 2}   # Saída
    ]
    arestas = [
        {"origemId": 1, "destinoId": 2, "peso": 1}  # Aresta simples
    ]
    
    # Criar o labirinto com dados simples
    criar_labirinto(dificuldade, vertices, arestas)