import sys
import logging

from pygame.locals import (
    KEYDOWN,
    K_ESCAPE,
    K_RIGHT,
    K_SPACE,
    K_b,
    QUIT,
)


EVENT_HANDLERS = {}

def _handle(event):
    def handler(fun):
        EVENT_HANDLERS[event] = fun
        return fun
    return handler

def handle_event(event, model, view):
    if hasattr(event, "type") and event.type in EVENT_HANDLERS:
        return EVENT_HANDLERS[event.type](event, model, view)

    if hasattr(event, "__hash__") and event in EVENT_HANDLERS:
        return EVENT_HANDLERS[event](event, model, view)

@_handle(KEYDOWN)
def keydown_handler(event, model, view):
    handle_event(event.key, model, view)

@_handle(QUIT)
@_handle(K_ESCAPE)
def keydown(event, model, view):
    logging.info("Bye!")
    sys.exit(0)

@_handle(K_RIGHT)
def update_model(event, model, view):
    model.update()

@_handle(K_SPACE)
def play_pause(event, model, view):
    view.toggle_auto_update()

@_handle(K_b)
def show_best(event, model, view):
    view.toggle_show_best()
