def criar_labirinto(dificuldade, vertices, arestas):
    payload = {
        "dificuldade": dificuldade,
        "vertices": vertices,
        "arestas": arestas
    }
    response = requests.post(f"{API_URL}/labirinto", json=payload)
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
