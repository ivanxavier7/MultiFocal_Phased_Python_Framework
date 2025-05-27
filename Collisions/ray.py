import numpy as np
import random
import json
from configs import SPEED_OF_SOUND, LOSS_PERCENTAGE, REFLECTION_DISPERSION_DEG, WRITE_INTERVAL, RESULT_SAVE_FRAMES

# Global buffer to store position and collision data
simulation_data = []

# Counter to track the number of frames processed
frame_counter = 0


def write_to_json():
    """
    Writes the buffered simulation data to 'posicoes.json'.
    """
    try:
        with open("posicoes.json", "w") as file:
            json.dump(simulation_data, file, indent=4)
    except Exception as e:
        print(f"Error saving simulation data: {e}")

class Ray:
    def __init__(self, sensor_pos, emission_angle_deg, sensor_id=0, color='blue',
                 loss_percentage=LOSS_PERCENTAGE, dispersion_deg=REFLECTION_DISPERSION_DEG):
        """
        Inicializa um raio com:
         - sensor_pos: posição do sensor (centro) de emissão.
         - emission_angle_deg: ângulo de emissão (graus).
         - sensor_id: identificador do sensor emissor.
         - color: cor do raio.
        """
        self.sensor_pos = np.array(sensor_pos)
        self.emission_angle_deg = emission_angle_deg
        self.emission_angle_rad = np.deg2rad(emission_angle_deg)
        self.direction = np.array([np.cos(self.emission_angle_rad), np.sin(self.emission_angle_rad)])
        self.sensor_id = sensor_id
        self.color = color
        self.loss_percentage = loss_percentage
        self.dispersion_deg = dispersion_deg

        # Dados de colisão e retorno
        self.has_collision = False
        self.collision_point = None
        self.t_out = None   # tempo de ida (sensor -> colisão)
        self.reflection_direction = None
        self.t_return = None  # tempo de retorno (colisão -> sensor)
        self.response_time = None
        # Lista de sensores que já detectaram este raio (para evitar duplicação)
        self.detected_by = []
        # Atributo para rastrear se o raio foi detectado
        self.detected = False

    def propagate(self, surface):
        """
        Calcula a colisão com a superfície.
         - Se houver colisão, calcula t_out e define a direção de retorno baseada na reflexão,
           considerando a inclinação da superfície.
        """
        try:
            result = surface.ray_intersection(self.sensor_pos, self.direction)
            if result is None:
                return
            t, collision_point, hit_segment = result
            self.has_collision = True
            self.collision_point = collision_point
            distance_out = np.linalg.norm(collision_point - self.sensor_pos)
            self.t_out = distance_out / SPEED_OF_SOUND

            # Save collision data to the in-memory buffer
            collision_data = {
                "angle_deg": self.emission_angle_deg,
                "collision_point": collision_point.tolist(),
                "t_out": self.t_out
            }
            if RESULT_SAVE_FRAMES > 0:
                simulation_data.append(collision_data)

            # Calcula a normal do segmento atingido:
            A, B = hit_segment
            seg_vec = B - A
            normal = np.array([seg_vec[1], -seg_vec[0]])
            normal = normal / np.linalg.norm(normal)
            # Garante que a normal aponta contra o vetor incidente:
            if np.dot(self.direction, normal) > 0:
                normal = -normal

            # Reflexão ideal: R = D - 2*(D·N)*N
            refl = self.direction - 2 * (np.dot(self.direction, normal)) * normal

            # Aplica dispersão aleatória
            delta_deg = random.uniform(-self.dispersion_deg, self.dispersion_deg)
            delta_rad = np.deg2rad(delta_deg)
            cos_d = np.cos(delta_rad)
            sin_d = np.sin(delta_rad)
            rot_matrix = np.array([[cos_d, -sin_d],
                                   [sin_d,  cos_d]])
            self.reflection_direction = rot_matrix.dot(refl)
            self.reflection_direction /= np.linalg.norm(self.reflection_direction)

            distance_return = np.linalg.norm(collision_point - self.sensor_pos)
            self.t_return = distance_return / (SPEED_OF_SOUND * (1 - self.loss_percentage))
            self.response_time = self.t_out + self.t_return
        except Exception as e:
            print(f"Error during ray propagation (angle {self.emission_angle_deg:.1f}°): {e}")

    def position_at_time(self, t_global):
        """
        Retorna a posição do raio no tempo t_global (segundos) desde a emissão.
         - Se t_global <= t_out, está na fase de ida.
         - Se t_global > t_out, segue a trajetória de retorno.
        """
        global frame_counter
        try:
            if not self.has_collision or t_global <= self.t_out:
                # Fase de ida (out phase)
                pos = self.sensor_pos + self.direction * SPEED_OF_SOUND * t_global
                # Save position during 'out' phase
                position_data = {
                    "angle_deg": self.emission_angle_deg,
                    "phase": "out",
                    "position": pos.tolist(),
                    "time": t_global
                }
            else:
                # Fase de retorno (return phase)
                t_prime = t_global - self.t_out
                pos = self.collision_point + self.reflection_direction * (SPEED_OF_SOUND * (1 - self.loss_percentage)) * t_prime
                # Save position during 'return' phase
                position_data = {
                    "angle_deg": self.emission_angle_deg,
                    "phase": "return",
                    "position": pos.tolist(),
                    "time": t_global
                }

            if RESULT_SAVE_FRAMES > 0:
                # Append position data to the in-memory buffer
                simulation_data.append(position_data)

            # Increment frame counter and write to JSON periodically
            frame_counter += 1
            if RESULT_SAVE_FRAMES > 0 and frame_counter % WRITE_INTERVAL == 0:
                write_to_json()

            return pos
        except Exception as e:
            print(f"Error calculating position for Ray {self.emission_angle_deg:.1f}° at time {t_global:.2f}s: {e}")
            return self.sensor_pos

# Ensure this function is called at the end of the simulation to save remaining data
def save_simulation_data():
    """
    Writes the buffered simulation data to 'posicoes.json'.
    """
    if RESULT_SAVE_FRAMES > 0:
        write_to_json()