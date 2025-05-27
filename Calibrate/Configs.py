# Configuração dos parâmetros principais

TIME_MULTIPLIER = 0.2      # Fator para desacelerar a simulação (1 = tempo real, 0.1 = 10x mais devagar)
FREQUENCY_HZ = 8 * TIME_MULTIPLIER    # Frequência da onda (Hz)
SOUND_SPEED = 343 * TIME_MULTIPLIER   # Velocidade do som no ar (m/s)
LAMBDA0 = SOUND_SPEED / FREQUENCY_HZ # Comprimento de onda
N = 10                   # Número de emissores


# Lista de emissores: cada um com id, frequência, posição x e y
EMITTERS = [
    {"id": "E1", "freq": 8.0, "x": -2.0, "y": 0.0},
    {"id": "E2", "freq": 6.0, "x": 0.0, "y": 0.0},
    {"id": "E3", "freq": 8.0, "x": 2.0, "y": 0.0}
]

# Lista de emissores com foco: cada um com id, frequência, posição x e y
FOCAL_POINTS= [ 
    {"x": -5.0, "y": 0.0}, 
    {"x": -5.0, "y": 5.0}, 
    {"x": 5.0, "y": 5.0}, 
    {"x": 0.0, "y": 10.0}, 
    {"x": 8.0, "y": 4.0}, 
    {"x": 2.0, "y": -6.0}
]