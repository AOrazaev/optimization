import numpy
import numpy.random as random
import math
import copy

import logging


class SalesmanRoute(object):
    def __init__(self, config):
        self.num_towns = config['model']['num_towns']
        self.t0 = config['model']['T0']
        self.type = config['model']['type']
        self.window_size = numpy.array(config['window']['size'])

        assert self.num_towns > 1

        self.route = list(
            random.random(2) * self.window_size
            for _ in range(self.num_towns))

        self.nrg = self.energy()
        self.best = self.route
        self.best_nrg = self.nrg

        self.tick = 0
        self.iteration = 0

    def energy(self):
        nrg = math.hypot(*(self.route[0] - self.route[-1]))
        for x in range(len(self.route) - 1):
            nrg += math.hypot(*(self.route[x] - self.route[x + 1]))

        return nrg

    def tempreture(self, tick):
        if self.type == 'fast':
            return float(self.t0) / tick
        return float(self.t0) / math.log(1 + self.tick)

    def update(self):
        self.tick += 1
        self.iteration += 1
        T = self.tempreture(self.tick)
        logging.debug('-'*10 + ' iteration: {0} '.format(self.iteration) + '-'*10)
        logging.debug('TEMPRETURE({0}) = {1}'.format(self.tick, T))

        i0, i1 = random.randint(len(self.route), size=2)

        self.route[i0], self.route[i1] = self.route[i1], self.route[i0]
        new_nrg = self.energy()
        logging.debug('NEW ENERGY = {0}'.format(new_nrg))
        logging.debug('ENERGY = {0}'.format(self.nrg))
        logging.debug('BEST ENERGY = {0}'.format(self.best_nrg))

        if self.nrg > new_nrg:
            if self.best_nrg > new_nrg:
                self.best = copy.deepcopy(self.route)
                self.best_nrg = new_nrg
            self.nrg = new_nrg
        else:
            try:
                prob = math.exp(- (new_nrg - self.nrg) / T)
            except OverflowError:
                prob = 0
            logging.debug("MUTATION PROBABILITY = {0}".format(prob))
            if random.random() < prob:
                logging.debug("RANDOM MUTATION ACCURED")
                self.nrg = new_nrg
            else:
                self.tick -= 1
                self.route[i0], self.route[i1] = self.route[i1], self.route[i0]
