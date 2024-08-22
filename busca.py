from collections import deque

def flood_fill_maze(graph, ini, fim):
    visitado = set()  
    queue = deque([(ini, [ini])])  
    while queue:
        node, cam = queue.popleft()
        
        if node == fim:
            return cam  
        
        if node not in visitado:
            visitado.add(node)
            
            for visinho in graph[node]:
                if visinho not in visitado:
                    queue.append((visinho, cam + [visinho]))

    return None  

# Exemplo de uso
graph = {
    '1': ['2', '3'],
    '2': ['1', '4', '5'],
    '3': ['1', '6'],
    '4': ['2'],
    '5': ['2', '6'],
    '6': ['3', '5', '7'],
    '7': ['6']
}

ini = '4'
fim = '7'

cam_fim = flood_fill_maze(graph, ini, fim)
if cam_fim:
    print("Caminho encontrado:", " -> ".join(cam_fim))
else:
    print("Caminho não encontrado")
