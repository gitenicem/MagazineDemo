from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from machine.StateMachine import StateMachine


# noinspection PyTypeHints
class State:
    name = 'no state'
    machine: StateMachine = None # type: ignore

    def __init__(self, machine: StateMachine):
        self.machine = machine

    def on_enter(self):
        """Acciones al entrar en el estado."""
        pass

    def on_exit(self):
        """Acciones al salir del estado."""
        pass

    def update(self):
        """Actualización del estado, transiciones a otros estados."""
        pass



    def ready(self):
        pass

    def checking(self):
        pass

    def error_clear(self):
        pass

    def running(self):
        pass

    def alarmed(self):
        pass
