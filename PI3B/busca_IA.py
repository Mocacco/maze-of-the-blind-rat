import heapq

# Representação do grafo do labirinto
grafo = {
    'A': {'B': 1, 'C': 4},
    'B': {'A': 1, 'D': 2, 'E': 5},
    'C': {'A': 4, 'F': 3},
    'D': {'B': 2},
    'E': {'B': 5, 'F': 1},
    'F': {'C': 3, 'E': 1}
}

# Função heurística (neste caso, usa uma heurística simplista)
def heuristic(node, chegada):
    return 1  # Mantém a heurística mínima para simplificar

# Algoritmo A* para grafos
def a_star(grafo, ini, chegada, output_file):
    open_list = []
    heapq.heappush(open_list, (0, ini))
    antigo = {}
    g_score = {ini: 0}
    f_score = {ini: heuristic(ini, chegada)}
    arestas_exp = []

    while open_list:
        atual = heapq.heappop(open_list)[1]

        # Verifica se chegamos ao nó de saída
        if atual == chegada:
            path = []
            while atual in antigo:
                path.append(atual)
                atual = antigo[atual]
            path.append(ini)
            path.reverse()
            
            # Salva as arestas exploradas em um arquivo .txt
            with open(output_file, 'w') as f:
                for aresta in arestas_exp:
                    f.write(f"{aresta[0]} -> {aresta[1]}\n")
            return path

        for viz in grafo[atual]:
            tentative_g_score = g_score[atual] + grafo[atual][viz]

            if viz not in g_score or tentative_g_score < g_score[viz]:
                antigo[viz] = atual
                g_score[viz] = tentative_g_score
                f_score[viz] = tentative_g_score + heuristic(viz, chegada)
                heapq.heappush(open_list, (f_score[viz], viz))

                # Registra a aresta explorada
                arestas_exp.append((atual, viz))

    # Salva as arestas exploradas em um arquivo .txt mesmo se não encontrar um caminho
    with open(output_file, 'w') as f:
        for aresta in arestas_exp:
            f.write(f"{aresta[0]} -> {aresta[1]}\n")
    return None  # Se não encontrar um caminho

# Executa o A* e imprime o caminho encontrado
inicio = 'A'
fim = 'F'
output_file = 'arestas_exploradas.txt'
path = a_star(grafo, inicio, fim, output_file)
if path:
    print("Caminho encontrado:", path)
else:
    print("Nenhum caminho encontrado")

# Confirmação de que as arestas foram salvas
print(f"Arestas exploradas foram salvas no arquivo: {output_file}")

