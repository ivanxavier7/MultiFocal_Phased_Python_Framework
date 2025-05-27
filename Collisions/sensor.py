# sensor.py
import numpy as np
import matplotlib.patches as patches

class Sensor:
    def __init__(self, sensor_id, position, rotation_deg, width=0.6, height=0.3,
                 emission_range_deg=(60, 120), emission_step_deg=5, frequency=1.0, color='blue',
                 initial_delay=0.0):
        """
        Parâmetros:
         - sensor_id: identificador do sensor.
         - position: posição [x,y] (centro do sensor).
         - rotation_deg: direção central de emissão (graus).
         - emission_range_deg: intervalo angular total para os raios.
         - emission_step_deg: espaçamento angular entre partículas.
         - frequency: frequência de emissão em Hz (número de emissões por segundo).
         - color: cor dos raios emitidos.
         - initial_delay: atraso inicial (em segundos) para a primeira emissão.
        """
        self.sensor_id = sensor_id
        self.position = np.array(position)
        self.rotation_deg = rotation_deg
        self.width = width
        self.height = height
        self.frequency = frequency
        self.color = color
        self.emission_range_deg = emission_range_deg
        self.emission_step_deg = emission_step_deg
        self.initial_delay = initial_delay  # novo parâmetro

    def emit_rays(self):
        """
        Emite um pulso de raios a partir do centro do sensor.
        """
        try:
            min_angle = self.rotation_deg - (self.emission_range_deg[1] - self.emission_range_deg[0]) / 2.0
            max_angle = self.rotation_deg + (self.emission_range_deg[1] - self.emission_range_deg[0]) / 2.0
            angles = np.arange(min_angle, max_angle + self.emission_step_deg, self.emission_step_deg)
            from ray import Ray  # Importação local para evitar dependência circular
            rays = []
            for angle in angles:
                ray = Ray(self.position, angle, sensor_id=self.sensor_id, color=self.color)
                rays.append(ray)
            print(f"Sensor {self.sensor_id}: Emitted {len(rays)} rays.")
            return rays
        except Exception as e:
            print(f"Error during ray emission for Sensor {self.sensor_id}: {e}")
            return []

    def contains(self, point):
        """
        Verifica se um ponto [x,y] está dentro do retângulo do sensor.
        """
        x, y = point
        cx, cy = self.position
        return (cx - self.width / 2 <= x <= cx + self.width / 2) and (cy - self.height / 2 <= y <= cy + self.height / 2)

    def draw(self, ax):
        """
        Desenha o sensor como um retângulo e exibe seu ID.
        """
        sensor_rect = patches.Rectangle((self.position[0] - self.width/2, self.position[1] - self.height/2),
                                        self.width, self.height,
                                        linewidth=1, edgecolor=self.color, facecolor='none')
        ax.add_patch(sensor_rect)
        ax.text(self.position[0], self.position[1], f"Sensor {self.sensor_id}", color=self.color,
                fontsize=10, ha='center', va='center')
