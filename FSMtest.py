import pytest
import os
import sys
from FSM.State import State
from FSM.Event import Event
from FSM.Machine import Machine
from enum import Enum

# define child classes (functionality could be extended)
class UserState(State):
    def __init__(self, name, state_function = None):
        super().__init__(name, state_function)

class UserEvent(Event):
    def __init__(self, event_type):
        super().__init__(event_type=event_type)

# initialize logic as required in assignment1
state_idle = UserState("idle")
state_e1_1_time = UserState("state_e1_1_time")
state_e1_2_times = UserState("state_e1_2_times")
state_e1_3_times = UserState("state_e1_3_times", lambda : print("event1 received 3 times in a row"))
state_e2_1_time = UserState("state_e2_1_time")
state_e2_2_times = UserState("state_e2_2_times")
state_e2_3_times = UserState("state_e2_3_times", lambda : print("event2 received 3 times in a row"))

state_list = [state_idle, state_e1_1_time, state_e1_2_times, state_e1_3_times,
              state_e2_1_time, state_e2_2_times, state_e2_3_times]

EventTypes = Enum('myEventType', 'EvType1 EvType2')
transition_table = {
                    (state_idle.state_name, EventTypes.EvType1) : state_e1_1_time.state_name,
                    (state_idle.state_name, EventTypes.EvType2) : state_e2_1_time.state_name,
                    (state_e1_1_time.state_name, EventTypes.EvType2) : state_e2_1_time.state_name,
                    (state_e1_2_times.state_name, EventTypes.EvType2) : state_e2_1_time.state_name,
                    (state_e1_3_times.state_name, EventTypes.EvType2) : state_e2_1_time.state_name,
                    (state_e2_1_time.state_name, EventTypes.EvType1) : state_e1_1_time.state_name,
                    (state_e2_2_times.state_name, EventTypes.EvType1) : state_e1_1_time.state_name,
                    (state_e2_3_times.state_name, EventTypes.EvType1) : state_e1_1_time.state_name,
                    (state_e1_1_time.state_name, EventTypes.EvType1) : state_e1_2_times.state_name,
                    (state_e1_2_times.state_name, EventTypes.EvType1) : state_e1_3_times.state_name,
                    (state_e1_3_times.state_name, EventTypes.EvType1) : state_e1_1_time.state_name,
                    (state_e2_1_time.state_name, EventTypes.EvType2) : state_e2_2_times.state_name,
                    (state_e2_2_times.state_name, EventTypes.EvType2) : state_e2_3_times.state_name,
                    (state_e2_3_times.state_name, EventTypes.EvType2) : state_e2_1_time.state_name
                    }

example_machine = Machine(states_list=state_list, init_state_index=0, transition_table=transition_table)
example_machine.start()

def test_assignment1(capsys):
    """
    The machine should indicate (e.g. print a warning to the standard output) the first time it receives 3
    consecutive events of the same type.
    :param capsys:
    :return:
    """
    for i in range(10):
        example_machine.post_event(UserEvent(EventTypes.EvType1))

    example_machine.wait()
    out, err = capsys.readouterr()

    assert out == """event1 received 3 times in a row
event1 received 3 times in a row
event1 received 3 times in a row
"""
    assert err == ""
    assert example_machine.get_current_state() == "state_e1_1_time"

    for i in range(10):
        example_machine.post_event(UserEvent(EventTypes.EvType2))

    # store current state state_e2_1_time to file
    example_machine.wait()
    out, err = capsys.readouterr()

    assert err == ""
    assert out == """event2 received 3 times in a row
event2 received 3 times in a row
event2 received 3 times in a row
"""

    assert example_machine.get_current_state() == "state_e2_1_time"

def test_assignment2(capsys):
    """
    Make the machine persistent - save its "state" to a file and read it when the process
    starts so it can continue from where it left off. Assume that there will be more types of events/states
    in the future
    :param capsys:
    :return:
    """
    example_machine.store_state_to_file(path=os.path.join(os.getenv('APPDATA'), 'myMachineState.txt'))

    # move to state state_e2_3_times
    example_machine.post_event(UserEvent(EventTypes.EvType2))
    example_machine.post_event(UserEvent(EventTypes.EvType2))
    example_machine.wait()
    out, err = capsys.readouterr()

    assert out == """event2 received 3 times in a row\n"""
    assert err == ""
    assert example_machine.get_current_state() == "state_e2_3_times"

    # load state state_e2_1_time from the file
    example_machine.load_state_from_file(path=os.path.join(os.getenv('APPDATA'), 'myMachineState.txt'))
    example_machine.wait()

    assert example_machine.get_current_state() == "state_e2_1_time"

    # again move to state state_e2_3_times
    example_machine.post_event(UserEvent(EventTypes.EvType2))
    example_machine.post_event(UserEvent(EventTypes.EvType2))
    example_machine.wait()

    assert out == """event2 received 3 times in a row\n"""
    assert err == ""
    assert example_machine.get_current_state() == "state_e2_3_times"