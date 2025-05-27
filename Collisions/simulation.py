# simulation.py
import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from surface import Surface
from sensor import Sensor
from ray import Ray
from configs import SIMULATION_FRAMES, SIMULATION_TOTAL_TIME, PLOT_X_LIMITS, PLOT_Y_LIMITS

class Simulation:
    def __init__(self, surface_points, sensors, frames=SIMULATION_FRAMES):
        """
        Inicializa a simulação com:
         - surface_points: pontos que definem a superfície.
         - sensors: lista de objetos Sensor.
         - frames: número de frames para a animação.
        """
        try:
            self.surface = Surface(surface_points)
            self.sensors = sensors
            self.detections = []  # Armazena os eventos de detecção

            # Lista de grupos de emissão; cada grupo é um dict com:
            # { 'sensor_id': ..., 'rays': [...], 'markers': [...], 'emission_time': ... }
            self.emission_groups = []

            # Estatísticas de partículas emitidas e recebidas
            self.particle_stats = {sensor.sensor_id: {"emitted": 0, "received": {}} for sensor in sensors}
            for sensor in sensors:
                self.particle_stats[sensor.sensor_id]["received"] = {s.sensor_id: 0 for s in sensors}

            # Define o tempo da próxima emissão para cada sensor com base no initial_delay
            self.sensor_next_emission_time = {sensor.sensor_id: sensor.initial_delay for sensor in self.sensors}

            # Se o initial_delay for 0, emite logo no início (t = 0)
            for sensor in self.sensors:
                if sensor.initial_delay == 0.0:
                    rays = sensor.emit_rays()
                    self.particle_stats[sensor.sensor_id]["emitted"] += len(rays)
                    for ray in rays:
                        ray.propagate(self.surface)
                        for other_sensor in self.sensors:
                            if other_sensor.sensor_id != sensor.sensor_id and ray.detected_by:
                                self.particle_stats[other_sensor.sensor_id]["received"][sensor.sensor_id] += 1
                    self.emission_groups.append({
                        'sensor_id': sensor.sensor_id,
                        'rays': rays,
                        'markers': [],  # os marcadores serão criados no plot inicial
                        'emission_time': 0.0
                    })

            self.total_time = SIMULATION_TOTAL_TIME  # tempo total da simulação (em segundos)
            self.frames = frames
            self.detection_tolerance = 1.0  # tolerância para detecção (em metros)
        except Exception as e:
            print(f"Error during initialization: {e}")

    def save_particle_stats(self, filename="nrparticulas.json"):
        try:
            # Add sensor coordinates to the particle stats
            for sensor in self.sensors:
                self.particle_stats[sensor.sensor_id]["coordinates"] = {
                    "x": sensor.position[0],
                    "y": sensor.position[1]
                }

            # Calculate statistics for particles received
            total_received = sum(
                sum(stats["received"].values()) for stats in self.particle_stats.values()
            )
            left_received = sum(
                sum(stats["received"].values())
                for sensor_id, stats in self.particle_stats.items()
                if stats["coordinates"]["x"] < 0
            )
            center_received = sum(
                sum(stats["received"].values())
                for sensor_id, stats in self.particle_stats.items()
                if stats["coordinates"]["x"] == 0
            )
            right_received = sum(
                sum(stats["received"].values())
                for sensor_id, stats in self.particle_stats.items()
                if stats["coordinates"]["x"] > 0
            )

            # Calculate percentages
            left_percentage = (left_received / total_received) * 100 if total_received > 0 else 0
            center_percentage = (center_received / total_received) * 100 if total_received > 0 else 0
            right_percentage = (right_received / total_received) * 100 if total_received > 0 else 0

            # Add statistics to the JSON data
            stats_summary = {
                "statistics": {
                    "total_received": total_received,
                    "left": {"count": left_received, "percentage": round(left_percentage, 2)},
                    "center": {"count": center_received, "percentage": round(center_percentage, 2)},
                    "right": {"count": right_received, "percentage": round(right_percentage, 2)}
                }
            }

            # Combine particle stats and statistics summary
            combined_data = {**self.particle_stats, **stats_summary}

            # Convert all values to native Python types
            combined_data_native = json.loads(json.dumps(combined_data, default=lambda x: x.item() if hasattr(x, 'item') else x))

            # Save the combined data to JSON
            with open(filename, "w") as file:
                json.dump(combined_data_native, file, indent=4)

            # Print the statistics
            print("\n--- Particle Reception Statistics ---")
            print(f"Total particles received: {total_received}")
            print(f"Left (x < 0): {left_received} ({left_percentage:.2f}%)")
            print(f"Center (x = 0): {center_received} ({center_percentage:.2f}%)")
            print(f"Right (x > 0): {right_received} ({right_percentage:.2f}%)")
        except Exception as e:
            print(f"Error saving particle stats: {e}")

    def animate(self):
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_title("Simulação de Emissão de Partículas (Onda Sonora)")
            ax.set_xlabel("X (m)")
            ax.set_ylabel("Y (m)")
            ax.grid(True)
            ax.set_xlim(PLOT_X_LIMITS)
            ax.set_ylim(PLOT_Y_LIMITS)

            self.surface.draw(ax)
            for sensor in self.sensors:
                sensor.draw(ax)

            # Cria os marcadores para os grupos já emitidos
            for group in self.emission_groups:
                sensor_emissor = next(s for s in self.sensors if s.sensor_id == group['sensor_id'])
                group_markers = []
                for ray in group['rays']:
                    marker, = ax.plot(sensor_emissor.position[0], sensor_emissor.position[1], 'o',
                                      color=ray.color, markersize=4, alpha=0.7)
                    group_markers.append(marker)
                group['markers'] = group_markers

            def update(frame):
                try:
                    print(f"Updating frame {frame}/{self.frames - 1}")
                    t_global = (frame / (self.frames - 1)) * self.total_time
                    print(f"Global time: {t_global:.2f}s")
                    updated_artists = []

                    # Verifica se algum sensor deve emitir novos raios
                    for sensor in self.sensors:
                        period = 1.0 / sensor.frequency
                        next_time = self.sensor_next_emission_time[sensor.sensor_id]
                        if t_global >= next_time:
                            print(f"Sensor {sensor.sensor_id} emitindo novo pulso em t = {t_global:.2f}s")
                            new_rays = sensor.emit_rays()
                            self.particle_stats[sensor.sensor_id]["emitted"] += len(new_rays)
                            for ray in new_rays:
                                ray.propagate(self.surface)
                                for other_sensor in self.sensors:
                                    if other_sensor.sensor_id != sensor.sensor_id and ray.detected_by:
                                        self.particle_stats[other_sensor.sensor_id]["received"][sensor.sensor_id] += 1
                            # Cria marcadores para os novos raios
                            sensor_emissor = sensor
                            new_markers = []
                            for ray in new_rays:
                                marker, = ax.plot(sensor_emissor.position[0], sensor_emissor.position[1], 'o',
                                                  color=ray.color, markersize=4, alpha=0.7)
                                new_markers.append(marker)
                            # Adiciona o novo grupo de emissão
                            self.emission_groups.append({
                                'sensor_id': sensor.sensor_id,
                                'rays': new_rays,
                                'markers': new_markers,
                                'emission_time': t_global
                            })
                            # Atualiza o tempo da próxima emissão
                            self.sensor_next_emission_time[sensor.sensor_id] = t_global + period

                    # Atualiza a posição de todos os marcadores de cada grupo de emissão
                    for group in self.emission_groups:
                        t_local = t_global - group['emission_time']
                        for i, ray in enumerate(group['rays']):
                            try:
                                pos = ray.position_at_time(t_local)
                                if not np.allclose(group['markers'][i].get_data(), pos, atol=1e-2):
                                    group['markers'][i].set_data([pos[0]], [pos[1]])
                                    updated_artists.append(group['markers'][i])
                                # Detecção de eco (se o sensor receptor não for o emissor)
                                if ray.has_collision and t_local > ray.t_out:
                                    for sensor in self.sensors:
                                        if sensor.sensor_id == ray.sensor_id:
                                            continue
                                        if sensor.sensor_id not in ray.detected_by:
                                            if np.sum((pos - sensor.position)**2) < self.detection_tolerance**2:
                                                detection = {
                                                    'sensor_receptor': sensor.sensor_id,
                                                    'sensor_emissor': ray.sensor_id,
                                                    'emissor_coords': list(ray.sensor_pos),  # Corrigido para usar sensor_pos
                                                    'angulo': round(ray.emission_angle_deg, 1),
                                                    'tempo_ms': round(ray.response_time * 1000, 2)
                                                }
                                                self.detections.append(detection)
                                                ray.detected_by.append(sensor.sensor_id)
                                                self.particle_stats[sensor.sensor_id]["received"][ray.sensor_id] += 1
                                                print(f"Sensor {sensor.sensor_id} detectou eco do raio de {ray.emission_angle_deg:.1f}° "
                                                      f"emitido pelo Sensor {ray.sensor_id} com tempo de resposta {ray.response_time*1000:.2f} ms")
                            except Exception as e:
                                print(f"Error updating ray {i} from Sensor {group['sensor_id']} at frame {frame}: {e}")

                    return updated_artists
                except Exception as e:
                    print(f"Error during update frame {frame}: {e}")
                    return []

            anim = FuncAnimation(fig, update, frames=self.frames, interval=50, blit=True, repeat=False)
            plt.show()

            # Exporta as detecções para um arquivo JSON após a animação
            try:
                # Converte os dados para tipos nativos do Python
                results_native = json.loads(json.dumps(self.detections, default=lambda x: x.item() if hasattr(x, 'item') else x))
                with open("resultados.json", "w", encoding="utf-8") as f:
                    json.dump(results_native, f, indent=4, ensure_ascii=False)
                print(f"\nTotal de {len(self.detections)} ecos registados. Resultados guardados em 'resultados.json'.")
            except Exception as e:
                print(f"Error saving results to JSON: {e}")

            # Salva as estatísticas de partículas emitidas e recebidas
            self.save_particle_stats()
        except Exception as e:
            print(f"Error during animation setup: {e}")
