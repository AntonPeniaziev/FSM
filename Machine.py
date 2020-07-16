"""
A framework fot building final state machines
"""

from queue import Queue
from threading import Thread
from FSM.State import State
from FSM.Event import Event


class Machine:

    def __init__(self, states_list: list, init_state_index: int, transition_table: dict) -> object:
        """

        :param states_list:
        :param init_state_index:
        :param transition_table: a dictionary of type (state_name, event_type) => next_state_name
        """
        self.__states_dict = dict(zip([ev.state_name for ev in states_list], states_list))
        self.__current_state = states_list[init_state_index]
        self.__transition_table = transition_table
        self.__events_queue = Queue()

    def __pend_on_event(self, target_events):
        """
        blocks on any event type from target_events,
        ignores all other events
        :param target_events - list of event types:
        :return:
        """
        event = None
        while event is None or event.event_type not in target_events:
            event = self.__events_queue.get(block=True, timeout=None)
            self.__events_queue.task_done()

        return event

    def __get_active_events_for_state(self, state : State):
        """

        :param state:
        :return: all events types that can switch the machine state from 'state'
        """
        return [state_event_pair[1]
                  for state_event_pair in self.__transition_table.keys()
                  if state_event_pair[0] == state.state_name]

    def __dispatch_event(self, source_state : State, event : Event):
        """

        :param source_state:
        :param event:
        :return: the next state for source_state after 'event' received
        """

        return self.__states_dict[self.__transition_table[(source_state.state_name, event.event_type)]]

    def __run_machine(self):
        """
        worker function
        :return:
        """
        while True:
            if self.__current_state.state_function is not None:
                self.__current_state.state_function()
            event = self.__pend_on_event(target_events=self.__get_active_events_for_state(self.__current_state))
            self.__current_state = self.__dispatch_event(source_state=self.__current_state, event=event)


    def start(self):
        """
        starts state machine's thread
        :return:
        """
        Thread(target=self.__run_machine, daemon=True).start()

    def post_event(self, event):
        self.__events_queue.put(event)

    def wait(self):
        """
        wait until all events in queue are processed
        :return:
        """
        self.__events_queue.join()

    def get_current_state(self):
        return self.__current_state.state_name

    def store_state_to_file(self, path):
        with open(path, 'w') as file_handler:
            file_handler.write(self.__current_state.state_name)

    def load_state_from_file(self, path):
        with open(path, 'r') as file_handler:
            saved_state_name = file_handler.read()
            if saved_state_name not in self.__states_dict.keys():
                raise Exception("State machine does not have state " + saved_state_name)
            else:
                self.__current_state = self.__states_dict[saved_state_name]
