class DustParticle:
    # Ray-tracing only
    def __init__(self, fill='blue', density=0):
        self.fill = fill
        self.density = density
        self.visible = True
        self.shadows = 100

    def getColor(self, instance, x, y, z):
        return self.fill
