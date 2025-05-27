# configs.py
import numpy as np

# Parâmetros da simulação
SIMULATION_FRAMES = 300
SIMULATION_TOTAL_TIME = 5.0  # tempo total em segundos
PLOT_X_LIMITS = (-10, 10)
PLOT_Y_LIMITS = (-5, 15)

# Configurações dos sensores
SENSOR_CONFIGS = [
    {
        'sensor_id': 0,
        'position': [-2, 0],
        'rotation_deg': 90,
        'emission_range_deg': (60, 120),
        'emission_step_deg': 5,
        'frequency': 8.0,      # emite a cada 2s
        'color': 'red',
        'initial_delay': 0.09526810779246189   # Calculado com a outra script
    },
    {
        'sensor_id': 1,
        'position': [0, 0],
        'rotation_deg': 90,
        'emission_range_deg': (60, 120),
        'emission_step_deg': 5,
        'frequency': 6.0,     # emite a cada 1s
        'color': 'blue',
        'initial_delay': 0.12779397473275023
    },
    {
        'sensor_id': 2,
        'position': [2, 0],
        'rotation_deg': 90,
        'emission_range_deg': (60, 120),
        'emission_step_deg': 5,
        'frequency': 8.0,     # emite a cada 1s n ondas
        'color': 'green',
        'initial_delay': 0.09526810779246189
    }
]

# Parâmetros dos raios
# ray.py settings
SPEED_OF_SOUND = 34.3  # m/s    10x mais lento para facilitar a captura de colisões
LOSS_PERCENTAGE = 0.2
REFLECTION_DISPERSION_DEG = 5
WRITE_INTERVAL = 60
RESULT_SAVE_FRAMES = 0  # 0 significa não salvar os resultados de posição/colisão
FOCAL_POINTS= [ 
    {"x": 0.0, "y": 10.0}, 
]