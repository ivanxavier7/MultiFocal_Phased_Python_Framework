import numpy as np

class Surface:
    def __init__(self, points):
        """
        Inicializa a superfície a partir de uma lista de pontos [x, y] (vértices).
        """
        self.points = np.array(points)
        self.segments = [(self.points[i], self.points[i+1]) for i in range(len(self.points)-1)]

    def ray_intersection(self, origin, direction):
        """
        Calcula a interseção do raio (origin + t * direction, t>=0) com cada segmento da superfície.
        Retorna (t, ponto de colisão, segmento) do primeiro encontro ou None.
        """
        min_t = float('inf')
        collision_point = None
        hit_segment = None
        for seg in self.segments:
            A, B = seg
            result = self._intersect_ray_segment(origin, direction, A, B)
            if result is not None:
                t, point = result
                if t < min_t:
                    min_t = t
                    collision_point = point
                    hit_segment = seg
        if collision_point is not None:
            return min_t, collision_point, hit_segment
        return None

    def _intersect_ray_segment(self, origin, direction, A, B):
        """
        Calcula a interseção entre um raio e um segmento.
        Se houver interseção válida (t>=0 e u em [0,1]), retorna (t, ponto).
        """
        seg_vec = B - A
        denom = direction[0]*seg_vec[1] - direction[1]*seg_vec[0]
        if abs(denom) < 1e-6:
            return None
        diff = A - origin
        t = (diff[0]*seg_vec[1] - diff[1]*seg_vec[0]) / denom
        u = (diff[0]*direction[1] - diff[1]*direction[0]) / denom
        if t >= 0 and 0 <= u <= 1:
            return t, origin + t * direction
        return None

    def draw(self, ax):
        """
        Desenha a superfície.
        """
        ax.plot(self.points[:,0], self.points[:,1], 'k-', lw=2)
