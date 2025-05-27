import numpy as np
import matplotlib.pyplot as plt
from Configs import LAMBDA0

class EmitterArray:
    def __init__(self):
        self.emitters = []
    
    def AddEmitter(self, emitter):
        self.emitters.append(emitter)
    
    def Increment(self, dt):
        for emitter in self.emitters:
            emitter.Increment(dt)
    
    def GetCircles(self):
        circles = []
        for emitter in self.emitters:
            circles.extend(emitter.circles)
        return circles
    
    def RemoveOffset(self):
        if not self.emitters:
            return
        offsets = [emitter.t0 for emitter in self.emitters]
        offset_min = np.min(offsets)
        for emitter in self.emitters:
            emitter.Increment(offset_min)
    
    @property
    def circles(self):
        return self.GetCircles()
    
    def Visualize(self, title="Visualization"):
        """
        Visualiza a simulação dos emissores usando animação.
        Cada emissor é representado por vários círculos (ondas) que se expandem conforme o tempo.
        """
        fig, ax = plt.subplots()
        ax.set_title(title)
        ax.set_xlim(-50, 50)
        ax.set_ylim(-10, 50)
        ax.set_aspect('equal')
        
        # Adiciona todos os círculos ao gráfico
        for emitter in self.emitters:
            for circle in emitter.circles:
                ax.add_patch(circle)
        
        from matplotlib.animation import FuncAnimation
        FPS = 30

        def init():
            # Retorna todos os círculos de uma única vez (lista flat)
            return self.GetCircles()

        def update(frame):
            self.Increment(1 / FPS)
            return self.GetCircles()

        anim = FuncAnimation(fig, update, init_func=init, interval=1000 / FPS, blit=True)
        # Guarda a animação para evitar que seja coletada pelo garbage collector
        self.anim = anim  
        plt.show()


class Emitter:
    def __init__(self, x, y, c, f, phase, rMax=100, color="tab:blue", alpha=0.6):
        """
        Inicializa um emissor com:
         - x, y: posição do emissor,
         - c: velocidade de propagação,
         - f: frequência,
         - phase: fase inicial,
         - rMax: raio máximo da onda gerada,
         - color: cor para visualização,
         - alpha: transparência.
         
        Fórmulas:
          - Comprimento de onda: λ₀ = c / f
          - Período: T = 1 / f (usado para sincronização das ondas)
        """
        self.r = np.array([x, y])
        self.c = c
        self.f = f
        self.rMax = rMax
        self.alpha = alpha
        self.color = color
        self.SetUp()  # Configura os parâmetros da onda e cria os círculos
        self.SetPhase(phase)  # Define a fase inicial
    
    def Increment(self, dt):
        """
        Avança a simulação do emissor em um intervalo de tempo dt.
        A distância percorrida pela onda é dada por: r = i * λ₀ + Wrap( (λ₀*φ/(2π)) + c*t, λ₀)
        onde a velocidade efetiva pode ser ajustada multiplicando c por um TIME_MULTIPLIER
        (já incorporado via ajuste dos parâmetros físicos em Configs.py).
        """
        self.t += dt
        if self.t < self.t0:
            return
        
        for i, circle in enumerate(self.circles):
            r = i * self.lambda0 + self.Wrap(self.lambda0 * self.phi / (2 * np.pi) + self.c * self.t, self.lambda0)
            circle.set_height(2 * r)
            circle.set_width(2 * r)
            circle.set_alpha(self.alpha if i < ((self.t - self.t0) / self.T) else 0)
    
    def SetPhase(self, phi):
        """
        Define a fase inicial do emissor e ajusta o tempo inicial (t0) para sincronização.
        Fórmula: t0 = T * (1 - φ/(2π))
        """
        self.phi = self.Wrap(phi, 2 * np.pi)
        self.t0 = self.T * (1 - self.phi / (2 * np.pi))
        self.t = 0
    
    def SetUp(self):
        """
        Configura os parâmetros do emissor e cria os círculos que representam as ondas.
        Fórmulas:
          - λ₀ = c / f  (comprimento de onda)
          - T = 1 / f   (período)
        """
        self.lambda0 = self.c / self.f
        self.T = 1. / self.f
        self.N = int(np.ceil(self.rMax / self.lambda0))
        self.circles = [plt.Circle(xy=tuple(self.r), fill=False, lw=2,
                                   radius=0, alpha=self.alpha, color=self.color)
                        for i in range(self.N)]
    
    def Wrap(self, x, x_max):
        """
        Garante que x esteja no intervalo [0, x_max].
        """
        if x >= 0:
            return x - np.floor(x / x_max) * x_max
        else:
            return x_max - (-x - np.floor(-x / x_max) * x_max)
    
    def CalculatePhaseFromFocus(self, x_focus, y_focus):
        """
        Calcula a fase necessária para focalizar a onda em (x_focus, y_focus).
        Fórmula: φ = (2π/λ₀) * d, onde d é a distância entre o emissor e o ponto focal.
        """
        d = np.sqrt(np.sum((self.r - np.array([x_focus, y_focus]))**2))
        return (2 * np.pi / LAMBDA0) * d
