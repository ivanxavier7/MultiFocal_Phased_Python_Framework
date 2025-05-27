import json
import numpy as np
from collections import defaultdict

SPEED_OF_SOUND = 343.0  # m/s
OUTLIERS_PERCENTAGE = 30
TEMPO_PERDA_TOTAL = 0.0
CALIBRAR_PERDAS_LATERAIS = 1.0
CALIBRAR_PERDAS_ORIGEM = 0.78

def load_results(filename="resultados.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar o arquivo {filename}: {e}")
        return []


def filtrar_outliers_porcentagem(valores, porcentagem=OUTLIERS_PERCENTAGE):
    if len(valores) == 0:
        return []
    media = np.mean(valores)
    distancias = [abs(v - media) for v in valores]
    indices_ordenados = np.argsort(distancias)
    n_total = len(valores)
    n_remover = int((porcentagem / 100) * n_total)
    indices_filtrados = indices_ordenados[:-n_remover] if n_remover > 0 else indices_ordenados
    return [valores[i] for i in indices_filtrados]


def calcular_cateto_maior(hipotenusa, cateto_menor):
    if hipotenusa <= cateto_menor:
        return 0.0
    return np.sqrt(hipotenusa ** 2 - cateto_menor ** 2)


def estatisticas_por_sensor(results, speed_of_sound=SPEED_OF_SOUND):
    global TEMPO_PERDA_TOTAL  # Declare TEMPO_PERDA_TOTAL as global
    grupos = defaultdict(list)
    tempos_origem = []

    for event in results:
        receptor = event["sensor_receptor"]
        emissor = event["sensor_emissor"]
        coords = tuple(event["emissor_coords"])
        tempo = event["tempo_ms"]
        chave = (receptor, emissor, coords)
        grupos[chave].append(tempo)
        if coords == (0, 0):
            tempos_origem.append(tempo)

    tempo_medio_origem = np.mean(filtrar_outliers_porcentagem(tempos_origem))
    estatisticas = {}

    for (receptor, emissor, coords), tempos in grupos.items():
        tempos_filtrados = filtrar_outliers_porcentagem(tempos)
        media_filtrada = np.mean(tempos_filtrados)
        distancia_filtrada = (media_filtrada / 1000) * speed_of_sound / 2

        cateto_menor = abs(coords[0])
        cateto_maior = calcular_cateto_maior(distancia_filtrada, cateto_menor)

        # Correção pela diferença do tempo do sensor na origem
        if coords != (0, 0):
            tempo_diferenca = media_filtrada - tempo_medio_origem
            TEMPO_PERDA_TOTAL += tempo_diferenca  # Modify the global variable
            distancia_corrigida = distancia_filtrada - ((tempo_diferenca / 1000) * speed_of_sound / 2)

        estatisticas[f"R{receptor}_E{emissor}_{coords}"] = {
            "tempo_medio_filtrado_ms": media_filtrada,
            "tempo_medio_origem_ms": tempo_medio_origem,
            "tempo_diferenca_ms": tempo_diferenca,
            "distancia_m_media_filtrada_m": distancia_filtrada,
            "distancia_corrigida_m": distancia_corrigida,
            "cateto_menor_m": cateto_menor,
            "cateto_maior_m": cateto_maior,
            "leituras_utilizadas": len(tempos_filtrados),
        }

    return estatisticas

def estatisticas_finais_sensor(results, speed_of_sound=SPEED_OF_SOUND):
    grupos = defaultdict(list)
    tempos_origem = []

    for event in results:
        receptor = event["sensor_receptor"]
        emissor = event["sensor_emissor"]
        coords = tuple(event["emissor_coords"])
        tempo = event["tempo_ms"]
        chave = (receptor, emissor, coords)
        grupos[chave].append(tempo)
        if coords == (0, 0):
            tempos_origem.append(tempo)
            
    estatisticas = {}

    for (receptor, emissor, coords), tempos in grupos.items():
        tempos_filtrados = filtrar_outliers_porcentagem(tempos)
        if coords != (0,0):
            media_filtrada = np.mean(tempos_filtrados) - TEMPO_PERDA_TOTAL * CALIBRAR_PERDAS_LATERAIS
        else:
            media_filtrada = np.mean(tempos_filtrados) - TEMPO_PERDA_TOTAL * CALIBRAR_PERDAS_ORIGEM
        distancia_filtrada = (media_filtrada / 1000) * speed_of_sound / 20

        estatisticas[f"R{receptor}_E{emissor}_{coords}"] = {
            "tempo_medio_filtrado_final_ms": media_filtrada,
            "distancia_m_media_final_m": distancia_filtrada,
        }

    return estatisticas

def load_statistics_from_json(filename="nrparticulas.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("statistics", {})
    except Exception as e:
        print(f"Erro ao carregar estatísticas do arquivo {filename}: {e}")
        return {}

def calcular_media_ponderada(stats_finais, json_stats):
    pesos = {
        "left": 1 - (json_stats.get("left", {}).get("percentage", 0) / 100),
        "center": 1 - (json_stats.get("center", {}).get("percentage", 0) / 100),
        "right": 1 - (json_stats.get("right", {}).get("percentage", 0) / 100),
    }
    soma_pesos = 0
    soma_ponderada = 0

    for chave, stat in stats_finais.items():
        coords = eval(chave.split("_")[-1])  # Extract coordinates from the key
        if coords[0] < 0:
            peso = pesos["left"]
        elif coords[0] == 0:
            peso = pesos["center"]
        else:
            peso = pesos["right"]

        soma_pesos += peso
        soma_ponderada += stat["distancia_m_media_final_m"] * peso

    return soma_ponderada / soma_pesos if soma_pesos > 0 else 0

def calcular_inclinacao_superficie(json_stats):
    left_percentage = json_stats.get("left", {}).get("percentage", 0)
    center_percentage = json_stats.get("center", {}).get("percentage", 0)
    right_percentage = json_stats.get("right", {}).get("percentage", 0)

    # Calculate inclination as a weighted difference
    inclinacao = (right_percentage - left_percentage) + (center_percentage * 0.5)
    return inclinacao

def main():
    results = load_results("resultados.json")
    if not results:
        print("Nenhum dado carregado. Verifique o arquivo.")
        return

    stats = estatisticas_por_sensor(results)
    print("\nEstatísticas por sensor:")
    for chave, stat in stats.items():
        print(f"\n{chave}:")
        for k, v in stat.items():
            print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
            
    stats_finais = estatisticas_finais_sensor(results)
    print("\nEstatísticas finais por sensor:")
    for chave, stat in stats_finais.items():
        print(f"\n{chave}:")
        for k, v in stat.items():
            print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")

    # Load and print statistics from JSON
    json_stats = load_statistics_from_json("nrparticulas.json")
    if json_stats:
        print(f"Total particles received: {json_stats.get('total_received', 0)}")
        print(f"Left (x < 0): {json_stats.get('left', {}).get('count', 0)} ({json_stats.get('left', {}).get('percentage', 0):.2f}%)")
        print(f"Center (x = 0): {json_stats.get('center', {}).get('count', 0)} ({json_stats.get('center', {}).get('percentage', 0):.2f}%)")
        print(f"Right (x > 0): {json_stats.get('right', {}).get('count', 0)} ({json_stats.get('right', {}).get('percentage', 0):.2f}%)")

        # Calculate and print weighted average
        media_ponderada = calcular_media_ponderada(stats_finais, json_stats)
        print(f"\nMédia ponderada da distância final: {media_ponderada:.4f} m")

        # Calculate and print surface inclination
        inclinacao = calcular_inclinacao_superficie(json_stats)
        print(f"Inclinação da superfície: {inclinacao:.2f} graus")
    else:
        print("\nNenhuma estatística encontrada no JSON.")

if __name__ == "__main__":
    main()
