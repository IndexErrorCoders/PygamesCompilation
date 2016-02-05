#==========================================================================
#    PyForce 0.1.0
#    Copyright (C) 2010 Xueqiao Xu <xueqiaoxu@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#==========================================================================


from const import *

top = -100
bottom = RESOLUTION[1] + 100
left = -100
right = RESOLUTION[0] + 100


FLY_PATH = {
    # from top to bottom in a line
    'path_a_1': [[30, top], [30, bottom]],
    'path_a_2': [[60, top], [60, bottom]],
    'path_a_3': [[90, top], [90, bottom]],
    'path_a_4': [[120, top], [120, bottom]],
    'path_a_5': [[150, top], [150, bottom]],
    'path_a_6': [[180, top], [180, bottom]],
    'path_a_7': [[210, top], [210, bottom]],
    'path_a_8': [[240, top], [240, bottom]],
    'path_a_9': [[270, top], [270, bottom]],
    'path_a_10': [[300, top], [300, bottom]],
    'path_a_11': [[330, top], [330, bottom]],

    # from left top to right bottom in a line
    'path_b_1': [[left, 20], [right, 380]],
    'path_b_2': [[left, 50], [right, 410]],
    'path_b_3': [[left, 80], [right, 440]],

    # from right top to left bottom in a line
    'path_c_1': [[right, 20], [left, 380]],
    'path_c_2': [[right, 50], [left, 410]],
    'path_c_3': [[right, 80], [left, 440]],


    # from left top to right bottom in a curve
    'path_d_1': [[left, 70],[2, 70], [85, 90], [173, 143],[250, 233],
                 [266, 315], [266, bottom]],
    # from right top to left bottom in a curve
    'path_d_2': [[right, 70], [350, 60], [240, 80], [155, 133],
                 [112, 176], [82, 268], [82, bottom]],
    # from left bottom to right top in a curve
    'path_d_3': [[266, bottom], [266, 315], [250, 233], [173, 143],
                 [85, 90], [2, 70], [left, 70]],
    # from right bottom to left top in a curve
    'path_d_4': [[82, bottom], [82, 268], [112, 176], [155, 133],
                 [240, 80], [350, 60], [right, 70]],


    # from left top to right middle then to left bottom
    'path_e_1': [[left, 40], [1, 40], [113, 87], [281, 105], [298, 111],
                 [313, 130], [319, 152], [321, 272], [311, 305], [280, 320],
                 [93, 342], [31, 369], [left, 425]],
    # from right top to left middle then to right bottom
    'path_e_2': [[right, 79], [359, 79], [279, 94], [84, 121], [65, 132],
                 [59, 149], [54, 312], [59, 338], [74, 349], [292, 375],
                 [353, 393], [right, 393]],
    # from left bottom to right middle then to left top
    'path_e_3': [[left, 374], [1, 374], [21, 345], [36, 333], [56, 321],
                 [274, 298], [286, 298], [286, 291], [292, 282], [292, 273],
                 [298, 177], [296, 167], [288, 160], [272, 151], [95, 133],
                 [10, 120], [left, 83]],
    # from right bottom to left middle then to right top
    'path_e_4': [[right, 376], [357, 376], [312, 344], [301, 340], [286, 337],
                 [78, 326], [54, 321], [40, 308], [33, 291], [31, 233],
                 [33, 220], [48, 209], [70, 202], [287, 186], [354, 168],
                 [right, 148]]

}