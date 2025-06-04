#!/usr/bin/env python3
"""Simple 3D platformer using Panda3D.

Controls:
- W/A/S/D: move
- SPACE: jump
- ESC: quit

Install dependencies with:
    pip install panda3d
"""

from panda3d.core import AmbientLight, DirectionalLight, Vec3
from panda3d.core import CollisionNode, CollisionSphere, CollisionTraverser
from panda3d.core import CollisionHandlerPusher, CollisionBox, BitMask32
from direct.showbase.ShowBase import ShowBase
from direct.task import Task


class Platformer(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        # Lighting
        ambient = AmbientLight('ambient')
        ambient.setColor((0.7, 0.7, 0.7, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        dlight = DirectionalLight('dlight')
        dlight.setColor((0.8, 0.8, 0.8, 1))
        dlight_np = self.render.attachNewNode(dlight)
        dlight_np.setHpr(45, -45, 0)
        self.render.setLight(dlight_np)

        # Player
        self.player = self.loader.loadModel('models/box')
        self.player.reparentTo(self.render)
        self.player.setScale(0.5)
        self.player.setPos(0, 0, 2)

        # Physics parameters
        self.gravity = -9.81
        self.jump_speed = 8
        self.move_speed = 5
        self.velocity = Vec3(0, 0, 0)

        # Collisions
        self.traverser = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()

        player_solid = CollisionSphere(0, 0, 0, 0.5)
        player_node = CollisionNode('player')
        player_node.addSolid(player_solid)
        player_np = self.player.attachNewNode(player_node)
        player_np.setCollideMask(BitMask32.bit(0))

        self.traverser.addCollider(player_np, self.pusher)
        self.pusher.addCollider(player_np, self.player)

        # Floor
        floor = self.loader.loadModel('models/box')
        floor.reparentTo(self.render)
        floor.setScale(10, 10, 0.5)
        floor.setPos(0, 0, -0.5)

        floor_solid = CollisionBox((-10, -10, -0.5), (10, 10, 0))
        floor_node = CollisionNode('floor')
        floor_node.addSolid(floor_solid)
        floor_np = floor.attachNewNode(floor_node)
        floor_np.setCollideMask(BitMask32.bit(0))

        # City decor with moving cars
        self.cars = []
        self.car_speed = 4
        self.setup_city()

        # Simple platform
        platform = self.loader.loadModel('models/box')
        platform.reparentTo(self.render)
        platform.setScale(3, 3, 0.5)
        platform.setPos(5, 5, 2)

        plat_solid = CollisionBox((-3, -3, -0.5), (3, 3, 0))
        plat_node = CollisionNode('platform')
        plat_node.addSolid(plat_solid)
        plat_np = platform.attachNewNode(plat_node)
        plat_np.setCollideMask(BitMask32.bit(0))

        # Coin
        coin = self.loader.loadModel('models/smiley')
        coin.setScale(0.5)
        coin.reparentTo(self.render)
        coin.setPos(5, 5, 3)
        coin.setTag('coin', '1')

        coin_solid = CollisionSphere(0, 0, 0, 0.5)
        coin_node = CollisionNode('coin')
        coin_node.addSolid(coin_solid)
        coin_np = coin.attachNewNode(coin_node)
        coin_np.setCollideMask(BitMask32.bit(1))

        self.coins = [coin]

        coin_handler = CollisionHandlerPusher()
        self.traverser.addCollider(player_np, coin_handler)
        coin_handler.addCollider(player_np, coin, base.drive.node())

        # Set up camera
        self.camera.reparentTo(self.player)
        self.camera.setPos(0, -10, 3)
        self.camera.setHpr(0, -10, 0)

        # Input
        self.accept('escape', self.close)
        self.accept('space', self.do_jump)
        self.key_map = {"w": False, "a": False, "s": False, "d": False}
        for key in self.key_map:
            self.accept(key, self.update_key, [key, True])
            self.accept(f'{key}-up', self.update_key, [key, False])

        self.taskMgr.add(self.update, 'update')

    def setup_city(self):
        """Create a simple city scene with moving cars."""
        # Road
        road = self.loader.loadModel('models/box')
        road.reparentTo(self.render)
        road.setScale(20, 3, 0.1)
        road.setPos(0, -6, 0)
        road.setColor(0.2, 0.2, 0.2, 1)

        # Buildings along the road
        for x in range(-9, 10, 3):
            for side in (-1, 1):
                building = self.loader.loadModel('models/box')
                building.reparentTo(self.render)
                building.setScale(1.5, 1.5, 5)
                building.setPos(x, -6 + side * 4, 2.5)
                building.setColor(0.6, 0.6, 0.6, 1)

        # Two simple cars moving back and forth
        for start_x in (-8, 8):
            car = self.loader.loadModel('models/box')
            car.reparentTo(self.render)
            car.setScale(0.7, 1.5, 0.4)
            car.setPos(start_x, -6, 0.4)
            car.setColor(1, 0, 0, 1)
            self.cars.append({'node': car, 'dir': 1 if start_x < 0 else -1})

    def update_key(self, key, value):
        self.key_map[key] = value

    def close(self):
        self.userExit()

    def do_jump(self):
        if abs(self.velocity.z) < 0.001:
            self.velocity.z = self.jump_speed

    def update(self, task):
        dt = globalClock.getDt()
        move = Vec3(0, 0, 0)
        if self.key_map["w"]:
            move.y += self.move_speed * dt
        if self.key_map["s"]:
            move.y -= self.move_speed * dt
        if self.key_map["a"]:
            move.x -= self.move_speed * dt
        if self.key_map["d"]:
            move.x += self.move_speed * dt
        self.player.setPos(self.player, move)

        # Gravity
        self.velocity.z += self.gravity * dt
        self.player.setZ(self.player.getZ() + self.velocity.z * dt)

        self.traverser.traverse(self.render)

        # Move cars along the road
        for car in self.cars:
            node = car['node']
            node.setX(node.getX() + car['dir'] * self.car_speed * dt)
            if node.getX() > 9:
                car['dir'] = -1
            elif node.getX() < -9:
                car['dir'] = 1

        # Reset vertical velocity if on ground
        if self.player.getZ() <= 0:
            self.player.setZ(0)
            if self.velocity.z < 0:
                self.velocity.z = 0

        # Check for coin collection
        for coin in list(self.coins):
            if (self.player.getPos() - coin.getPos()).length() < 1:
                coin.removeNode()
                self.coins.remove(coin)
                print("Coin collected!")

        return Task.cont


if __name__ == '__main__':
    game = Platformer()
    game.run()
