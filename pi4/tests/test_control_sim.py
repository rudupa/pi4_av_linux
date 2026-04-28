from pi4.src.models import VehicleState, PerceptionInputs
from pi4.src.control import planner, controller
from pi4.src.sim import step


def test_sim_step_progresses_state():
    s = VehicleState(mode="auto")
    p = PerceptionInputs(objects=[])
    plan = planner(p, "auto")
    cmd = controller(s, plan)
    s2 = step(s, cmd, 0.1)
    assert s2.speed_mps >= 0.0
