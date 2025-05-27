# main.py
import numpy as np
from sensor import Sensor
from simulation import Simulation
from configs import SENSOR_CONFIGS

# Define os pontos da superfície (barreira)
surface_points = np.array([
    [10, 5],
    [1, 5],
    [0, 13],
    [-1, 5],
    [-10, 5]
])

# Cria os sensores a partir dos dados de configuração
sensors = []
for conf in SENSOR_CONFIGS:
    sensor = Sensor(
        sensor_id=conf['sensor_id'],
        position=conf['position'],
        rotation_deg=conf['rotation_deg'],
        emission_range_deg=conf['emission_range_deg'],
        emission_step_deg=conf['emission_step_deg'],
        frequency=conf['frequency'],
        color=conf['color'],
        initial_delay=conf['initial_delay']
    )
    sensors.append(sensor)

# Cria e executa a simulação
sim = Simulation(surface_points, sensors)
sim.animate()
