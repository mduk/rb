#!/usr/bin/env python3


import sys


NORTH = 0
EAST = 90
SOUTH = 180
WEST = 270

LEFT = -90
RIGHT = 90


class Position:
    def __init__(self, x, y, s):
        self.x = x
        self.y = y
        self.s = s

    def __repr__(self):
        if self.s == 0:
            s = "N"
        elif self.s == 90:
            s = "E"
        elif self.s == 180:
            s = "S"
        else:
            s = "W"

        return "{} {} {}".format(self.x, self.y, s)


class Rover:
    def __init__(self, terrain):
        self._terrain = terrain
        self._commands = {
            "F": self._forwards,
            "L": self._left,
            "R": self._right,
        }

        def __repr__(self):
            return "<Rover id={}>".format(id(self))

    def command(self, command):
        if command not in self._commands:
            raise Exception("Unknown command: {}".format(command))

        return self._commands.get(command)()

    def _forwards(self):
        self._terrain.advance(self, 1)

    def _left(self):
        self._terrain.turn(self, LEFT)

    def _right(self):
        self._terrain.turn(self, RIGHT)


class PositionOutOfBoundsException(Exception):
    position = None

    def __init__(self, msg, position):
        self.position = position


class FellOffTheWorldException(PositionOutOfBoundsException):
    pass


class Terrain:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self._rovers = {}

    def __repr__(self):
        return "<Terrain id={}, x={}, y={}, n_rovers={}>".format(
            id(self), self.x, self.y, len(self._rovers)
        )

    def position(self, x, y, s):
        if x < 0 or y < 0 or x > self.x or y > self.y:
            raise PositionOutOfBoundsException(
                "Position {}x{} falls outside of bounds {}x{}".format(
                    x, y, self.x, self.y
                ),
                Position(x, y, s),
            )

        if s >= 360:
            s = s - 360

        if s < 0:
            s = s + 360

        return Position(x, y, s)

    def position_of(self, rover):
        _rover, position = self._rovers[id(rover)]
        return position

    def place_rover(self, rover, position):
        self._rovers[id(rover)] = (rover, position)

    def turn(self, rover, s):
        rover, position = self._rovers[id(rover)]
        new_position = self.position(position.x, position.y, position.s + s)
        self._rovers[id(rover)] = (rover, new_position)

    def advance(self, rover, steps):
        rover, old_position = self._rovers[id(rover)]

        try:
            if old_position.s is NORTH:
                self._rovers[id(rover)] = (rover, self.position(
                    x=old_position.x,
                    y=old_position.y + steps,
                    s=old_position.s,
                ))
            elif old_position.s is EAST:
                self._rovers[id(rover)] = (rover, self.position(
                    x=old_position.x + steps,
                    y=old_position.y,
                    s=old_position.s,
                ))
            elif old_position.s is SOUTH:
                self._rovers[id(rover)] = (rover, self.position(
                    x=old_position.x,
                    y=old_position.y - steps,
                    s=old_position.s,
                ))
            elif old_position.s is WEST:
                self._rovers[id(rover)] = (rover, self.position(
                    x=old_position.x - steps,
                    y=old_position.y,
                    s=old_position.s,
                ))
        except PositionOutOfBoundsException as e:
            raise FellOffTheWorldException("", e.position)


class Interpreter:
    def __init__(self, input_stream=sys.stdin, output_stream=sys.stdout):
        self._input_stream = input_stream
        self._output_stream = output_stream
        self._terrain = False
        self._compass = {"N": 0, "E": 90, "S": 180, "W": 270}

    def run(self):
        for line in self._input_stream:
            line = line.rstrip()

            if line == "":
                continue

            if self._terrain is False:
                x, y = line.split(" ")
                self._terrain = Terrain(int(x), int(y))
                continue

            tokens = line.split(" ")
            n_tokens = len(tokens)

            if n_tokens == 3:
                x, y, s = tokens
                rover = Rover(self._terrain)
                position = self._terrain.position(
                    int(x), int(y), self._compass[s]
                )
                self._terrain.place_rover(rover, position)
                continue

            if n_tokens == 1:
                try:
                    for c in tokens[0]:
                        rover.command(c)
                except FellOffTheWorldException:
                    self._output_stream.write(
                        "{} LOST\n".format(self._terrain.position_of(rover))
                    )
                else:
                    self._output_stream.write(
                        "{}\n".format(self._terrain.position_of(rover))
                    )


if __name__ == "__main__":
    import io

    script = io.StringIO(
        """
5 3
1 1 E
RFRFRFRF

3 2 N
FRRFLLFFRRFLL

0 3 W
LLFFFLFLFL
    """
    )
    Interpreter(script).run()
