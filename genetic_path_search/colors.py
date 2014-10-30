# -*- coding: utf-8 -*-

from singleton import Singleton


@Singleton
class Colors(object):
    def __init__(self):
        self._colordict = {}

    def set_colordict(self, new_dict):
        self._colordict = new_dict

    def get(self, color_name):
        return self._colordict.get(color_name)

def to_color(color_name):
    return Colors().get(color_name)

