from server.enemy import Enemy

class EnemyManager():

    def __init__(self):
        self.enemies = {
            1: Enemy(1, 100, 100, "green-slime"),
            2: Enemy(2, 150, 400, "green-slime"),
        }

    