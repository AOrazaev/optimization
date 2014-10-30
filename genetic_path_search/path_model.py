# -*- coding: utf-8 -*-

import numpy
import numpy.random as random
import math
import logging
import copy


def distance_to_section_from_circle(point1, point2, area):
    center, R = area
    center = numpy.array(center)

    ao = center - point1
    bo = center - point2
    ab = point2 - point1

    k = sum(ao * ab) / math.hypot(*ab)**2
    EPS = 0.00001
    if abs(k) > EPS and abs(k - 1) < EPS:
        ac = k * math.hypot(*ab)
        r = math.sqrt(math.hypot(*ao)**2 - ac**2)
    else:
        r = min(math.hypot(*ao), math.hypot(*bo))

    return max(0, R - r)


class Individual(list):
    def __init__(self, *args, **kwargs):
        super(Individual, self).__init__(*args, **kwargs)
        self._cost = None
        self._penalty_points = None
        self._length = None
        self._penalty_areas = []

    @property
    def cost(self):
        if self._cost is None:
            self._cost = self._calc_cost()
        return self._cost

    @property
    def penalty_points(self):
        if self._penalty_points is None:
            self.cost
        return self._penalty_points

    @property
    def length(self):
        if self._length is None:
            self._length = self._calc_length()
        return self._length

    def make_child(self, woman):
        men = self

        child_len = int((len(men) + len(woman)) / 2)
        total_cost = men.cost + woman.cost

        child = Individual([men[0]])
        child.set_penalty_areas(men._penalty_areas)

        for point_num in range(1, child_len - 1):
            ratio = float(point_num) / (child_len - 1)
            first_point = men.point_by_ratio(ratio)
            second_point = woman.point_by_ratio(ratio)

            k = min(men.cost, woman.cost) * (0.6 * random.random() - 0.3)
            child.append(first_point * ((men.cost - k) / total_cost) +
                         second_point * ((woman.cost + k) / total_cost))
        child.append(men[-1])

        return child

    def set_penalty_areas(self, areas):
        self._penalty_areas = areas
        self._cost = None  # Need to recalculate cost

    def __lt__(self, other):
        return self.cost < other.cost

    def _calc_length(self):
        result = 0.
        for x in range(1, len(self)):
            result += math.hypot(*(self[x] - self[x - 1]))
        return result

    def point_by_ratio(self, ratio):
        left = int(self.length * ratio)
        current = 1
        while left > 0:
            length = math.hypot(*(self[current - 1] - self[current]))
            if left < length:
                coeff = float(left) / length
                return self[current - 1] * coeff + self[current] * (1. - coeff)
            left -= length
            current += 1
            if current == len(self):
                return self[-1]

    def _calc_cost(self, delta=10.):
        cost = self.length
        self._penalty_points = []
        steps = self.length / delta
        for x in (x / steps for x in range(1, int(steps))):
            current = self.point_by_ratio(x)
            for center, R in self._penalty_areas:
                dist = math.hypot(*(current - numpy.array(center)))
                if dist < R:
                    self._penalty_points.append(numpy.array(current, dtype=int))
                    break
        return cost * math.exp(len(self.penalty_points))

    def mutate(self, prob, diviation):
        if (len(self) == 2):
            prob = prob / 3
        else:
            prob = prob / (len(self) - 2) / 3

        # Change point mutation
        if len(self) > 5:
            while prob > random.random():
                x = random.randint(2, len(self) - 3)
                mutation = diviation * random.randn(2)
                self[x] += mutation * 0.5
                self[x - 1] += mutation * 0.2
                self[x + 1] += mutation * 0.2

        # Add point mutation
        while prob > random.random():
            x = random.choice(range(0, len(self) - 1))
            middle = (self[x] + self[x + 1]) / 2
            self.insert(x + 1, middle + diviation * random.randn(2))

        # Remove point mutation
        while len(self) > 2 and prob > random.random():
            remove_index = random.choice(range(1, len(self) - 1, 1))
            del self[remove_index]

class PathModel(object):
    def __init__(self, config):
        self.start = config['model']['start']
        self.destination = config['model']['destination']
        self.population = []
        self.mutation_probability = config['model']['mutation_probability']
        self.mutate_best = config['model']['mutate_best']
        self.next_point_diviation = config['model']['next_point_diviation']
        self.population_size = config['model']['population_size']
        self.points_in_path = config['model']['points_in_path']
        self.num_to_choose = config['model']['num_to_choose']
        self.maxX, self.maxY = config['window']['size']

        self.generation = 1

        self.penalty_areas = config['model']['penalty_areas']
        self._initialize()
        self.log_generation_info()

    def check_point(self, point):
        if point[0] > self.maxX or point[1] > self.maxY:
            return False
        if point[0] < 0 or point[1] < 0:
            return False

    def mirror_point(self, point):
        result = numpy.array(point)
        if point[0] > self.maxX:
            result[0] = 2 * self.maxX - point[0]
        if point[1] > self.maxY:
            result[1] = 2 * self.maxY - point[1]
        return abs(result)

    def _initialize(self):
        for line_num in range(self.population_size):
            num_points = random.randint(*self.points_in_path)
            self.population.append(Individual([numpy.array(self.start)]))
            for point_num in range(num_points - 2):
                new_point = (self.next_point_diviation * random.randn(2) +
                             self.population[-1][-1])
                new_point = self.mirror_point(new_point)
                self.population[-1].append(new_point)
            self.population[-1].append(numpy.array(self.destination))
            self.population[-1].set_penalty_areas(self.penalty_areas)
        self.population.sort()

    def log_generation_info(self):
        n = self.num_to_choose
        logging.info("="*10 + " Generation: {0} ".format(self.generation) + "="*10)
        costs = [i.cost for i in self.population[:n]]
        logging.info("Best costs: {0}".format(costs))
        p = numpy.array([1. / c for c in costs])
        p = p / sum(p)
        logging.info("Probabilities: {0}".format(p))

    def evolution(self):
        num_selected = self.num_to_choose

        costs = [i.cost for i in self.population[:num_selected]]
        best = self.population[:num_selected]
        scores = [1. / (c + 500) for c in costs]
        p = numpy.array(scores)
        p = p / sum(p)

        self.population = [best[0]]
        for i in range(self.mutate_best):
            best_copy = copy.deepcopy(best[0])
            self.population.append(best_copy)
            self.population[-1].mutate(
                self.mutation_probability,
                self.next_point_diviation)

        for i in range(self.population_size - 1 - self.mutate_best):
            x = random.choice(range(num_selected), 1)[0]
            y = random.choice(range(num_selected), 1)[0]
            self.population.append(best[x].make_child(best[y]))
            self.population[-1].mutate(
                self.mutation_probability,
                self.next_point_diviation)
        self.population.sort()
        self.generation += 1
        self.log_generation_info()

    def crossover(self, first, second):
        child_len = int((len(first) + len(second)) / 2)
        sum_cost = first.cost + second.cost

        child = Individual([first[0]])
        child.set_penalty_areas(self.penalty_areas)
        for point_num in range(1, child_len - 1):
            ratio = float(point_num) / (child_len - 1)
            first_point = self.point_on_the_path_by_ratio(first, ratio)
            second_point = self.point_on_the_path_by_ratio(second, ratio)

            #child.append(first_point * k + second_point * (1 - k))
            child.append(first_point * (first_cost / sum_cost) +
                         second_point * (second_cost / sum_cost))
        child.append(first[-1])

        return child
