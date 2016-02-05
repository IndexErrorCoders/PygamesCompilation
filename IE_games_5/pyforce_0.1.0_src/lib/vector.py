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


from math import *

class Vector:
    def __init__(self, pos_1, pos_2):
        self.x = float(pos_2[0] - pos_1[0])
        self.y = float(pos_2[1] - pos_1[1])
        self.normal = hypot(self.x, self.y)
        if self.normal != 0:
            self.unit = (self.x / self.normal, self.y / self.normal)
            if self.y != 0:
                self.degree = degrees(atan(self.x / self.y))
                if self.y < 0:
                    self.degree = 180 + self.degree
            else:
                if self.x > 0:
                    self.degree = 90.0
                else:
                    self.degree = -90.0
        else:
            self.unit = (0, 0)
            self.degree = 0

VECTOR = (
    Vector((0, 0), (0, 2)),
    Vector((0, 0), (1, sqrt(3))),
    Vector((0, 0), (sqrt(3), 1)),
    Vector((0, 0), (2, 0)),
    Vector((0, 0), (sqrt(3), -1)),
    Vector((0, 0), (1, -sqrt(3))),
    Vector((0, 0), (0, -2)),
    Vector((0, 0), (-1, -sqrt(3))),
    Vector((0, 0), (-sqrt(3), -1)),
    Vector((0, 0), (-2, 0)),
    Vector((0, 0), (-sqrt(3), 1)),
    Vector((0, 0), (-1, sqrt(3)))
)