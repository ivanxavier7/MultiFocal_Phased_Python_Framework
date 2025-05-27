import os
import json
import numpy as np
from Emitter import Emitter, EmitterArray
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from Configs import LAMBDA0 as lambda0, SOUND_SPEED as c, FREQUENCY_HZ as f_hz, EMITTERS, FOCAL_POINTS

# DEMO 1 - Linear Array of Emitters
def demo1(emitter_array, N):
    xs = np.linspace(-lambda0/4, lambda0/4, N)
    ys = np.zeros_like(xs)
    phi = np.linspace(0, np.pi/2, N)
    for i in range(N):
        e = Emitter(xs[i], ys[i], c, f_hz, phi[i])
        emitter_array.AddEmitter(e)

# DEMO 2 - Linear Array of Emitters (Rotacionado)
def demo2(emitter_array, N):
    r = np.linspace(-lambda0/4, lambda0/4, N)
    angle = np.pi/4
    xs = r * np.cos(angle)
    ys = r * np.sin(angle)
    phi = np.linspace(0, np.pi/2, N)
    for i in range(N):
        e = Emitter(xs[i], ys[i], c, f_hz, phi[i])
        emitter_array.AddEmitter(e)

# DEMO 3 - Focussed Array
def demo3(emitter_array, N):
    xs = np.linspace(-lambda0, lambda0, N)
    ys = np.zeros_like(xs)
    for i in range(N):
        e = Emitter(xs[i], ys[i], c, f_hz, 0)
        phase = e.CalculatePhaseFromFocus(0, 20)
        e.SetPhase(phase)
        emitter_array.AddEmitter(e)

# DEMO 4 - Dual Frequency Emitters
def demo4(emitter_array, N):
    xs = np.linspace(-lambda0/4, lambda0/4, N)
    ys = np.zeros_like(xs)
    phi = np.linspace(0, np.pi/2, N)
    for i in range(N):
        e = Emitter(xs[i], ys[i], c, f_hz, phi[i])
        emitter_array.AddEmitter(e)
    for i in range(N):
        e = Emitter(xs[i], ys[i], c, 0.5 * f_hz, -phi[i], color="red")
        emitter_array.AddEmitter(e)

# DEMO 5 - Focussed Array com Dois Conjuntos
def demo5(emitter_array, N):
    xs = np.linspace(-lambda0, lambda0, N)
    ys = np.zeros_like(xs)
    # Conjunto 1: frequência f, focalizando em (0, 20)
    for i in range(N):
        e = Emitter(xs[i], ys[i], c, f_hz, 0)
        phase = e.CalculatePhaseFromFocus(0, 20)
        e.SetPhase(phase)
        emitter_array.AddEmitter(e)
    # Conjunto 2: frequência 0.8f, cor vermelha, focalizando em (-20, 30)
    for i in range(N):
        e = Emitter(xs[i], ys[i], c, 0.8 * f_hz, 0, color="red")
        phase = e.CalculatePhaseFromFocus(-20, 30)
        e.SetPhase(phase)
        emitter_array.AddEmitter(e)

# DEMO 6 - Focussed Array Random
def demo6(emitter_array, N):
    xs = np.random.uniform(-lambda0/2, lambda0/2, N)
    ys = np.random.uniform(-lambda0/2, lambda0/2, N)
    for i in range(N):
        e = Emitter(xs[i], ys[i], c, f_hz, 0)
        phase = e.CalculatePhaseFromFocus(0, 20)
        e.SetPhase(phase)
        emitter_array.AddEmitter(e)

# DEMO 7 - Focussed Array Random com Mais Emissores
def demo7(emitter_array, N):
    xs = np.random.uniform(-2*lambda0, 2*lambda0, N)
    ys = np.random.uniform(-2*lambda0, 2*lambda0, N)
    for i in range(N):
        e = Emitter(xs[i], ys[i], c, f_hz, 0)
        phase = e.CalculatePhaseFromFocus(0, 20)
        e.SetPhase(phase)
        emitter_array.AddEmitter(e)

def demo8(emitter_array, N):
    # Define as posições iniciais dos emissores (ao longo do eixo x)
    xs = np.linspace(-lambda0, lambda0, N)
    ys = np.zeros_like(xs)

    # Define os pontos focais a partir da configuração
    focal_points = [(point["x"], point["y"]) for point in FOCAL_POINTS]
    # Lista de cores para cada grupo de foco
    colors = [
        "blue", "red", "green", "orange", "purple", "yellow", "cyan", "magenta",
        "lime", "pink", "teal", "gold", "brown", "navy", "violet", "gray"
    ]

    # Inicialmente, cria um grupo de emissores com foco no primeiro ponto
    fx, fy = focal_points[0]
    initial_color = colors[0]
    for i in range(N):
        from Emitter import Emitter  # import local se necessário
        emitter = Emitter(xs[i], ys[i], c, f_hz, 0, color=initial_color)
        phase = emitter.CalculatePhaseFromFocus(fx, fy)
        emitter.SetPhase(phase)
        emitter_array.AddEmitter(emitter)

    # Variável de controle para o índice do foco atual (usamos lista para mutabilidade)
    current_focus_idx = [0]

    FPS = 30

    fig, ax = plt.subplots()
    ax.set_title(f"Foco: ({fx}, {fy}) | Ângulo: {np.degrees(np.arctan2(fy, fx)):.2f}°")
    ax.set_xlim(-60, 60)
    ax.set_ylim(-10, 60)
    ax.set_aspect('equal')

    # Adiciona os círculos de todos os emissores ao gráfico
    for circle in emitter_array.circles:
        ax.add_patch(circle)

    # Adiciona marcador para o ponto focal
    focus_dot, = ax.plot(fx, fy, 'ro', markersize=6)

    def init():
        return emitter_array.circles + [focus_dot]

    def calculate_focus_point(frame):
        t_total = frame / FPS
        idx = int(t_total // 2)  # 2 segundos por grupo
        if idx < len(focal_points):
            return focal_points[idx]
        return focal_points[-1]

    def update(frame):
        fx, fy = calculate_focus_point(frame)  # Certifique-se de que fx e fy sejam sequências
        focus_dot.set_data([fx], [fy])  # Envolva fx e fy em listas

        # Determina o foco atual com base no número de frames; aqui, cada grupo dura 2 segundos
        t_total = frame / FPS
        idx = int(t_total // 2)  # 2 segundos por grupo

        if idx < len(focal_points) and idx != current_focus_idx[0]:
            # Se for um novo foco, cria um novo grupo de emissores sem apagar os anteriores
            current_focus_idx[0] = idx
            fx, fy = focal_points[idx]
            color = colors[idx % len(colors)]
            print(f"Ponto focal: ({fx}, {fy}) | Ângulo: {np.degrees(np.arctan2(fy, fx)):.2f}°")
            ax.set_title(f"Foco: ({fx}, {fy}) | Ângulo: {np.degrees(np.arctan2(fy, fx)):.2f}°")
            focus_dot.set_data([fx], [fy])

            for i in range(N):
                from Emitter import Emitter
                new_emitter = Emitter(xs[i], ys[i], c, f_hz, 0, color=color)
                new_phase = new_emitter.CalculatePhaseFromFocus(fx, fy)
                new_emitter.SetPhase(new_phase)
                emitter_array.AddEmitter(new_emitter)
                for circle in new_emitter.circles:
                    ax.add_patch(circle)

        emitter_array.Increment(1 / FPS)
        return emitter_array.circles + [focus_dot]

    anim = FuncAnimation(fig, update, init_func=init, interval=1000 / FPS, blit=True, cache_frame_data=False)
    plt.animation_ref = anim
    plt.show()


# Demo9.py
def demo9():
    emitter_array = EmitterArray()

    for cfg in EMITTERS:
        e = Emitter(x=cfg["x"], y=cfg["y"], c=c, f=cfg["freq"], phase=0)
        e.id = cfg["id"]
        emitter_array.AddEmitter(e)

    focal_points = [(point["x"], point["y"]) for point in FOCAL_POINTS]

    results = {}

    for fx, fy in focal_points:
        key = f"{fx},{fy}"
        results[key] = []
        for emitter in emitter_array.emitters:
            phase = emitter.CalculatePhaseFromFocus(fx, fy)
            emitter.SetPhase(phase)
            results[key].append({
                "emitter_id": emitter.id,
                "x": emitter.r[0],
                "y": emitter.r[1],
                "freq": emitter.f,
                "phase_shift": phase,
                "initial_delay": emitter.t0
            })

    os.makedirs("results", exist_ok=True)

    with open("results/emitter_focus_config.json", "w") as f:
        json.dump(results, f, indent=4)

    print("Arquivo 'results/emitter_focus_config.json' gerado com sucesso.")
