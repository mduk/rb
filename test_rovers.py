import pytest
import io

from rovers import (
    Terrain,
    Position,
    PositionOutOfBoundsException,
    Rover,
    FellOffTheWorldException,
    Interpreter,
    NORTH,
    SOUTH,
)


@pytest.fixture
def terrain():
    return Terrain(5, 3)


@pytest.fixture
def rover(terrain):
    return Rover(terrain)


def test_terrain_positions(terrain):
    p = terrain.position(0, 0, 0)
    assert isinstance(p, Position)

    p2 = terrain.position(terrain.x, terrain.y, 0)
    assert isinstance(p2, Position)

    with pytest.raises(PositionOutOfBoundsException):
        terrain.position(-1, -1, 0)

    with pytest.raises(PositionOutOfBoundsException):
        terrain.position(terrain.x + 1, terrain.y + 1, 0)


def test_rover_placement(terrain, rover):
    terrain.place_rover(rover, terrain.position(1, 2, 0))
    position = terrain.position_of(rover)
    assert position.x == 1
    assert position.y == 2
    assert position.s == 0

    with pytest.raises(PositionOutOfBoundsException):
        terrain.place_rover(rover, terrain.position(-1, -1, 0))

    with pytest.raises(PositionOutOfBoundsException):
        terrain.place_rover(
            rover, terrain.position(terrain.x + 1, terrain.y + 1, 0)
        )


def test_rover_movement(terrain, rover):
    initial_position = terrain.position(0, 0, 0)
    terrain.place_rover(rover, initial_position)

    step = 1
    terrain.advance(rover, step)
    second_position = terrain.position_of(rover)
    assert second_position.x == initial_position.x
    assert second_position.y == initial_position.y + step
    assert second_position.s == initial_position.s
    assert second_position.y == 1

    turn = 180
    terrain.turn(rover, turn)
    third_position = terrain.position_of(rover)
    assert third_position.x == second_position.x
    assert third_position.y == second_position.y
    assert third_position.s == second_position.s + turn
    assert third_position.s == 180

    turn = -90
    terrain.turn(rover, turn)
    fourth_position = terrain.position_of(rover)
    assert fourth_position.x == third_position.x
    assert fourth_position.y == third_position.y
    assert fourth_position.s == third_position.s + turn
    assert fourth_position.s == 90

    step = 2
    terrain.advance(rover, step)
    fifth_position = terrain.position_of(rover)
    assert fifth_position.x == fourth_position.x + step
    assert fifth_position.y == fourth_position.y
    assert fifth_position.s == fourth_position.s

    with pytest.raises(FellOffTheWorldException):
        terrain.advance(rover, terrain.x)


def test_interpreter():
    script = io.StringIO("""
4 5
1 1 N
FRFLF

3 3 S
FFFFFF
    """)
    output_buffer = io.StringIO()
    i = Interpreter(input_stream=script, output_stream=output_buffer)
    i.run()

    assert i._terrain.x == 4
    assert i._terrain.y == 5

    assert len(i._terrain._rovers) == 2

    (rover_id, (rover, position)) = i._terrain._rovers.popitem() # Kali Ma!
    assert position.x == 3
    assert position.y == 0
    assert position.s == SOUTH

    (rover_id, (rover, position)) = i._terrain._rovers.popitem() # Kali Ma!
    assert position.x == 2
    assert position.y == 3
    assert position.s == NORTH

    lines = output_buffer.getvalue().split("\n")
    assert lines[0] == "2 3 N"
    assert lines[1] == "3 0 S LOST"
