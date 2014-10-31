import os
import yaml
import pygame
import argparse
import logging

from colors import *
from model import *

import event_handler


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


class Chart(CommonSprite):
    def __init__(self, config):
        super(Chart, self).__init__((0, 0), config['window']['size'])
        self.bgcolor = config['view']['bgcolor']
        self.town_color = config['view']['town_color']
        self.town_size = config['view']['town_size']
        self.road_color = config['view']['road_color']
        self.best_road_color = config['view']['road_color']

        self._show_best = False
        self._auto_update = False

    def toggle_auto_update(self):
        self._auto_update = not self._auto_update

    def toggle_show_best(self):
        self._show_best = not self._show_best

    def redraw(self, model):
        self.image.fill(to_color(self.bgcolor))

        for town in model.route:
            pygame.draw.circle(
                self.image,
                to_color(self.town_color),
                numpy.array(town, dtype=int),
                self.town_size)

        if self._show_best:
            pygame.draw.lines(
                self.image,
                to_color(self.best_road_color),
                True,
                model.best,
                2)
        else:
            pygame.draw.lines(
                self.image,
                to_color(self.road_color),
                True,
                model.route,
                2)


def init_window(config):
    pygame.init()
    window = pygame.display.set_mode(config['window']['size'], pygame.HWSURFACE)
    pygame.display.set_caption(config['window']['caption'])
    return window


def loop(window, config):
    chart = Chart(config)
    route = SalesmanRoute(config)
    while True:
        for event in pygame.event.get():
            event_handler.handle_event(event, route, chart)
        if chart._auto_update:
            route.update()

        pygame.display.set_caption(
            config['window']['caption'] + " TICK: {0}".format(route.tick))
        chart.redraw(route)
        chart.draw(window)
        pygame.display.flip()
        pygame.time.delay(5)

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
