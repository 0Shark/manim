#!/usr/bin/env python

import numpy as np
import itertools as it
from copy import deepcopy
import sys


from animation import *
from mobject import *
from constants import *
from region import *
from scene import Scene
from topics.complex_numbers import *

DEFAULT_PLANE_CONFIG = {
    "point_thickness" : 2*DEFAULT_POINT_THICKNESS


class SuccessiveComplexMultiplications(ComplexMultiplication):
    args_list = [
        (complex(1, 2), complex(1, -2)),
        (complex(-2, 1), complex(-2, -1)),
    ]

    @staticmethod
    def args_to_string(*multipliers):
        return "_".join([str(m)[1:-1] for m in  multipliers])

    @staticmethod
    def string_to_args(arg_string):
        args_string.replac("i", "j")
        return map(copmlex, arg_string.split())

    def construct(self, *multipliers):
        norm = abs(reduce(op.mul, multipliers, 1))
        shrink_factor = SPACE_WIDTH/max(SPACE_WIDTH, norm)
        plane_config = {
            "density" : norm*DEFAULT_POINT_DENSITY_1D,
            "unit_to_spatial_width" : shrink_factor,
            "x_radius" : shrink_factor*SPACE_WIDTH,
            "y_radius" : shrink_factor*SPACE_HEIGHT,
        }
        ComplexMultiplication.construct(self, multipliers[0], **plane_config)

        one_dot = self.draw_dot("1", 1, True)
        one_dot_copy = deepcopy(one_dot)

        for multiplier, count in zip(multipliers, it.count()):
            if multiplier == multipliers[0]:
                tex = "z"
            elif np.conj(multiplier) == multipliers[0]:
                tex = "\\bar z"
            else:
                tex = "z_%d"%count
            self.draw_dot(tex, multiplier)

        for multiplier in multipliers:
            self.multiplier = multiplier
            self.apply_multiplication()
            new_one = deepcopy(one_dot_copy)
            self.mobjects_to_move_without_molding.append(new_one)



class ShowComplexPower(SuccessiveComplexMultiplications):
    args_list = [
        (complex(0, 1), 1),
        (complex(0, 1), 2),
        (np.exp(complex(0, 2*np.pi/5)), 1),
        (np.exp(complex(0, 2*np.pi/5)), 5),
        (np.exp(complex(0, 4*np.pi/5)), 5),
        (np.exp(complex(0, -2*np.pi/5)), 5),
        (complex(1, np.sqrt(3)), 1),
        (complex(1, np.sqrt(3)), 3),
    ]

    @staticmethod
    def args_to_string(multiplier, num_repeats):
        start = ComplexMultiplication.args_to_string(multiplier)
        return start + "ToThe%d"%num_repeats

    @staticmethod
    def string_to_args(arg_string):
        parts = arg_string.split()
        if len(parts) < 2 or len(parts) > 3:
            raise Exception("Invalid arguments")
        multiplier = complex(parts[0])
        num_repeats = int(parts[1])
        return multiplier, num_repeats

    def construct(self, multiplier, num_repeats):
        SuccessiveComplexMultiplications.construct(
            [multiplier]*num_repeats
        )


class ComplexDivision(ComplexMultiplication):
    args_list = [
        complex(np.sqrt(3), 1),
        complex(1./3, -1./3),
        complex(1, 2),
    ]

    def construct(self, num):
        ComplexMultiplication.construct(self, 1./num)
        self.draw_dot("1", 1, False),
        self.draw_dot("z", num, True)
        self.apply_multiplication()

class ConjugateDivisionExample(ComplexMultiplication):
    args_list = [
        complex(1, 2),
    ]

    def construct(self, num):
        ComplexMultiplication.construct(self, np.conj(num), radius = 2.5*SPACE_WIDTH)
        self.draw_dot("1", 1, True)
        self.draw_dot("\\bar z", self.multiplier)
        self.apply_multiplication()
        self.multiplier = 1./(abs(num)**2)
        self.anim_config["interpolation_function"] = straight_path
        self.apply_multiplication()
        self.dither()

class DrawSolutionsToZToTheNEqualsW(Scene):
    @staticmethod
    def args_to_string(n, w):
        return str(n) + "_" + complex_string(w)

    @staticmethod
    def string_to_args(args_string):
        parts = args_string.split()
        return int(parts[0]), complex(parts[1])

    def construct(self, n, w):
        w = complex(w)
        plane_config = DEFAULT_PLANE_CONFIG.copy()
        norm = abs(w)
        theta = np.log(w).imag
        radius = norm**(1./n)
        zoom_value = (SPACE_HEIGHT-0.5)/radius
        plane_config["unit_to_spatial_width"] = zoom_value
        plane = ComplexPlane(**plane_config)
        circle = Circle(
            radius = radius*zoom_value,
            point_thickness = plane.point_thickness
        )
        solutions = [
            radius*np.exp(complex(0, 1)*(2*np.pi*k + theta)/n)
            for k in range(n)
        ]
        points = map(plane.number_to_point, solutions)
        dots = [
            Dot(point, color = BLUE_B, radius = 0.1)
            for point in points
        ]
        lines = [Line(*pair) for pair in adjascent_pairs(points)]

        self.add(plane, circle, *dots+lines)
        self.add(*plane.get_coordinate_labels())


class DrawComplexAngleAndMagnitude(Scene):
    args_list = [
        (
            ("1+i\\sqrt{3}", complex(1, np.sqrt(3)) ),
            ("\\frac{\\sqrt{3}}{2} - \\frac{1}{2}i", complex(np.sqrt(3)/2, -1./2)),
        ),
        (("1+i", complex(1, 1)),),
    ]
    @staticmethod
    def args_to_string(*reps_and_nums):
        return "--".join([
            complex_string(num) 
            for rep, num in reps_and_nums
        ])

    def construct(self, *reps_and_nums):
        radius = max([abs(n.imag) for r, n in reps_and_nums]) + 1
        plane_config = {
            "color" : "grey",
            "unit_to_spatial_width" : SPACE_HEIGHT / radius,
        }
        plane_config.update(DEFAULT_PLANE_CONFIG)
        self.plane = ComplexPlane(**plane_config)
        coordinates = self.plane.get_coordinate_labels()
        # self.plane.add_spider_web()
        self.add(self.plane, *coordinates)
        for rep, num in reps_and_nums:
            self.draw_number(rep, num)
            self.add_angle_label(num)
            self.add_lines(rep, num)

    def draw_number(self, tex_representation, number):
        point = self.plane.number_to_point(number)
        dot = Dot(point)
        label = TexMobject(tex_representation)
        max_width = 0.8*self.plane.unit_to_spatial_width
        if label.get_width() > max_width:
            label.scale_to_fit_width(max_width)
        dot_to_label_dir = RIGHT if point[0] > 0 else LEFT
        edge = label.get_edge_center(-dot_to_label_dir)
        buff = 0.1
        label.shift(point - edge + buff*dot_to_label_dir)
        label.highlight(YELLOW)

        self.add_mobjects_among(locals().values())


    def add_angle_label(self, number):
        arc = Arc(
            np.log(number).imag, 
            radius = 0.2
        )

        self.add_mobjects_among(locals().values())

    def add_lines(self, tex_representation, number):
        point = self.plane.number_to_point(number)
        x_line, y_line, num_line = [
            Line(
                start, end,
                color = color, 
                point_thickness = self.plane.point_thickness
            )
            for start, end, color in zip(
                [ORIGIN, point[0]*RIGHT, ORIGIN],
                [point[0]*RIGHT, point, point],
                [BLUE_D, GOLD_E, WHITE]
            )
        ]
        # tex_representation.replace("i", "")
        # if "+" in tex_representation:
        #     tex_parts = tex_representation.split("+")
        # elif "-" in tex_representation:
        #     tex_parts = tex_representation.split("-")
        # x_label, y_label = map(TexMobject, tex_parts)
        # for label in x_label, y_label:
        #     label.scale_to_fit_height(0.5)
        # x_label.next_to(x_line, point[1]*DOWN/abs(point[1]))
        # y_label.next_to(y_line, point[0]*RIGHT/abs(point[0]))
        norm = np.linalg.norm(point)
        brace = Underbrace(ORIGIN, ORIGIN+norm*RIGHT)
        if point[1] > 0:
            brace.rotate(np.pi, RIGHT)
        brace.rotate(np.log(number).imag)
        norm_label = TexMobject("%.1f"%abs(number))
        norm_label.scale(0.5)
        axis = OUT if point[1] > 0 else IN
        norm_label.next_to(brace, rotate_vector(point, np.pi/2, axis))

        self.add_mobjects_among(locals().values())

