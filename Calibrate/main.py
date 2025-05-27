# main.py

import matplotlib.pyplot as plt
from Emitter import EmitterArray
import Demos
from Configs import N

# Configurações gerais do matplotlib para melhorar a visualização
graph_size = 8
plt.rcParams["figure.figsize"] = (graph_size, graph_size)  # Tamanho da figura
txt_size = 14
plt.rcParams["font.size"] = txt_size  # Tamanho da fonte
plt.style.use('dark_background')  # Tema escuro

# Lista de funções demo disponíveis
demo_functions = [
    Demos.demo1,
    Demos.demo2,
    Demos.demo3,
    Demos.demo4,
    Demos.demo5,
    Demos.demo6,
    Demos.demo7,
    Demos.demo8,
]

def run_demos():
    for i, demo_func in enumerate(demo_functions):
        print(f"Executando Demo {i + 1}")
        ea = EmitterArray()
        # Usamos N emissores para cada demo
        demo_func(ea, N)
        ea.Visualize(title=f"Demo {i + 1}")

if __name__ == "__main__":
    Demos.demo9()
    run_demos()
