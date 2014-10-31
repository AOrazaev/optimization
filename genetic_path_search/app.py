#!/usr/bin/env python

import argparse
import os
import yaml
import pygame
import sys
import logging

import user_action

from colors import *
from path_model import *


class CommonSprite(pygame.sprite.Sprite):
    """CommonSprite -- common sprite for pygame app.
    """
    def __init__(self, position, size):
        """(CommonSprite, (int, int), (int, int)) -> NoneType
        """
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = pygame.Rect(position, size)

    def draw(self, surface):
        """(CommonSprite, pygame.Surface) -> NoneType
        """
        surface.blit(self.image, self.rect)

class FieldSprite(CommonSprite):
    def __init__(self, config):
        super(FieldSprite, self).__init__((0, 0), config['window']['size'])
        self._config = config
        self._show_best = False

    def toggle_show_best(self):
        self._show_best = not self._show_best

    def redraw(self, model):
        """(FieldSprite, PathModel) -> NoneType
        """
        self.image.fill(to_color(self._config['field']['color']))
        pygame.draw.circle(
            self.image,
            to_color(self._config['field']['start_color']),
            model.start,
            self._config['field']['point_size'])

        pygame.draw.circle(
            self.image,
            to_color(self._config['field']['destination_color']),
            model.destination,
            self._config['field']['point_size'])

        for area in model.penalty_areas:
            pygame.draw.circle(
                self.image,
                to_color(self._config['field']['penalty_area_color']),
                *area)

        for line in model.population:
            pygame.draw.lines(
                self.image,
                to_color(self._config['field']['path_color']),
                False,
                line)
            if self._show_best:
                break

        for line in model.population:
            for ppoint in line.penalty_points:
                pygame.draw.circle(
                    self.image,
                    to_color(self._config['field']['penalty_point_color']),
                    ppoint,
                    self._config['field']['penalty_point_size'])
            if self._show_best:
                break

def init_window(config):
    pygame.init()
    window = pygame.display.set_mode(config['window']['size'], pygame.HWSURFACE)
    pygame.display.set_caption(config['window']['caption'])
    return window



def handle_input(event):
    try:
        if handle_input.key_pressed:
            if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
                handle_input.key_pressed = False
                return user_action.NONE
            return handle_input.last_answer
    except AttributeError:
        pass

    if event.type == pygame.QUIT:
        return user_action.QUIT
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return user_action.QUIT

    if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
        handle_input.key_pressed = True
        handle_input.last_answer = user_action.RUN_EVOLUTION
        return user_action.RUN_EVOLUTION

    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        return user_action.RUN_EVOLUTION

    if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
        return user_action.TOGGLE_SHOW_BEST

    return user_action.NONE

def loop(window, config):
    field = FieldSprite(config)
    model = PathModel(config)
    pygame.event.wait()
    while True:
        field.redraw(model)
        field.draw(window)
        pygame.display.flip()
        action = handle_input(pygame.event.poll())
        if action == user_action.RUN_EVOLUTION:
            model.evolution()
        elif action == user_action.QUIT:
            break
        elif action == user_action.TOGGLE_SHOW_BEST:
            field.toggle_show_best()
        pygame.time.delay(10)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config',
        default=os.path.join(os.path.dirname(__file__), 'config.yaml'),
        type=argparse.FileType('rt'),
        help='path to config')

    args = parser.parse_args()
    args.config = yaml.load(args.config)
    Colors().set_colordict(args.config['colors'])
    return args

def main(args):
    window = init_window(args.config)
    loop(window, args.config)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(parse_args())
