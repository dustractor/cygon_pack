# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110 - 1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
"name":"Cygon Pack",
"author":"dustractor (this implementation only)",
"blender":(2,80,0),
"category":"Object"
}

import bpy
from copy import copy
from math import sqrt


class Rect(object):
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    def get_width(self):
        return abs(self.x2 - self.x1)
    def set_width(self, w):
        self.x2 = self.x1 + w
    def get_height(self):
        return abs(self.y2 - self.y1)
    def set_height(self, h):
        self.y2 = self.y1 + h
    def get_left(self):
        return self.x1
    def set_left(self, l):
        w = self.get_width()
        self.x1 = l
        self.x2 = l + w
    def get_top(self):
        return self.y2
    def set_top(self, t):
        h = self.get_height()
        self.y2 = t
        self.y1 = t - h
    def get_right(self):
        return self.x2
    def get_bottom(self):
        return self.y1
    def set_bottom(self, y1):
        h = self.get_height()
        self.y1 = y1
        self.y2 = self.y1 + h
    def offset(self, x, y):
        self.left = self.left + x
        self.top = self.top + y
        return self
    def inset(self, d):
        return Rect(self.x1 + d, self.y1 + d,
                    self.x2 - d, self.y2 - d)
    def inside(self, r):
        return self.x1 >= r.x1 and self.x2 <= r.x2\
               and self.y1 >= r.y1 and self.y2 <= r.y2
    width = property(fget=get_width, fset=set_width)
    height = property(fget=get_height, fset=set_height)
    left = property(fget=get_left, fset=set_left)
    top = property(fget=get_top, fset=set_top)
    right = property(fget=get_right)
    bottom = property(fget=get_bottom, fset=set_bottom)
    def __str__(self):
        return "[%f, %f, %f, %f]" % (self.x1, self.y1, self.x2, self.y2)
    def __repr__(self):
        return "Rect[%s]" % str(self)


class BinPackNode(object):
    def __init__(self, area):
        self.area = area
        self.leftchild = None
        self.rightchild = None
        self.filled = False
    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, str(self.area))
    def insert(self, newarea):
        if self.leftchild and self.rightchild:
            return (
                    self.leftchild.insert(newarea) or
                    self.rightchild.insert(newarea))
        if (
                self.filled or
                (newarea.width > self.area.width) or
                (newarea.height > self.area.height)):
            return None
        if (
                (self.area.width == newarea.width) and
                (self.area.height == newarea.height)):
            self.filled = True
            return self.area
        leftarea = copy(self.area)
        rightarea = copy(self.area)
        widthdifference = self.area.width - newarea.width
        heightdifference = self.area.height - newarea.height
        if widthdifference > heightdifference:
            leftarea.width = newarea.width
            rightarea.left = rightarea.left + newarea.width
            rightarea.width = rightarea.width - newarea.width
        else:
            leftarea.height = newarea.height
            rightarea.top = rightarea.top + newarea.height
            rightarea.height = rightarea.height - newarea.height
        self.leftchild = BinPackNode(leftarea)
        self.rightchild = BinPackNode(rightarea)
        return self.leftchild.insert(newarea)


def pack(oblist,margin):
    T_width = sum(ob.dimensions[0] for ob in oblist)
    T_height = sum(ob.dimensions[1] for ob in oblist)
    T_area = sum(ob.dimensions[0] * ob.dimensions[1] for ob in oblist)
    adjust = ( min(T_width,T_height) / max(T_width,T_height)) + margin
    side = int(sqrt(T_area) * adjust)
    obs = sorted( oblist,
            key=lambda ob:ob.dimensions[0] * ob.dimensions[1],
            reverse=True)
    Wdim,Hdim = [side]*2
    tree = BinPackNode(Rect(0, 0, Wdim,Hdim))
    for ob in obs:
        w,h,d = ob.dimensions
        r = Rect(0, 0, w, h)
        coords = tree.insert(r)
        if coords:
            ob.location[0] = coords.left
            ob.location[1] = coords.bottom


class CYGON_OT_cygon_pack_objects(bpy.types.Operator):
    bl_idname = "cygon.pack_objects"
    bl_label = "cygon pack objects"
    margin: bpy.props.FloatProperty(default = 0.1,precision=7)
    bl_options =  {"REGISTER","UNDO"}
    def execute(self,context):
        pack(context.selected_objects,self.margin)
        return {"FINISHED"}



def register():
    bpy.utils.register_class(CYGON_OT_cygon_pack_objects)

def unregister():
    bpy.utils.unregister_class(CYGON_OT_cygon_pack_objects)

