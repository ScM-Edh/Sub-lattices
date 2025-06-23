from qiskit_metal import draw, Dict
from qiskit_metal.toolbox_metal import math_and_overrides
from qiskit_metal.qlibrary.core import QComponent
import numpy as np

class FourWaysCap(QComponent):
    """
    Use this class as a template for your components - have fun

    Description:

    Options:
    """

    # Edit these to define your own template options for creation
    # Default drawing options
    default_options = Dict(
        width = '20um',
        finger_length = '50um',
        finger_width = '3um',
        cap_to_cpw = '5um',
        gap_to_gnd = '12um',
        cpw_length = '2um',
        pos_x='0um',
        pos_y='0um',
        orientation='0',
        layer='1'
    )
    """Default drawing options"""

    # Name prefix of component, if user doesn't provide name
    component_metadata = Dict(short_name='Four_ways_capacitor',
                             _qgeometry_table_poly='True',
                             _qgeometry_table_path='True')
    """Component metadata"""

    def make(self):
        """Convert self.options into QGeometry."""

        p = self.parse_options()  # Parse the string options into numbers

        # EDIT HERE - Replace the following with your code
        # Create some raw geometry
        # Use autocompletion for the `draw.` module (use tab key)
        # making the base of the capacitor
        
        #Defining the horizontal base of the capacitor
        cte = p.width*4
        horizontal = draw.rectangle(cte+2*p.finger_length, p.width, 0,0)
        rect2 = draw.rectangle(p.finger_length,p.width-2*p.finger_width,(cte+2*p.finger_length)/2-p.finger_length/2,0)
        rect3 = draw.rectangle(p.finger_length,p.width-2*p.finger_width,-(cte+2*p.finger_length)/2+p.finger_length/2,0)
        horizontal = draw.subtract(horizontal, rect2)
        horizontal = draw.subtract(horizontal, rect3)

        #Adding fingers
        finger1 = draw.rectangle(p.finger_length, p.finger_width, (cte+2*p.finger_length)/2-p.finger_length/2+p.cap_to_cpw, 0)
        finger2 = draw.rectangle(p.finger_length, p.finger_width, -(cte+2*p.finger_length)/2+p.finger_length/2-p.cap_to_cpw, 0)
        horizontal = draw.union(horizontal, finger1, finger2)

        #Defining the vertical part
        vertical = horizontal
        vertical = draw.rotate(vertical,90,origin=(0,0))

        #Add circle
        circle = draw.shapely.geometry.Point(0,0).buffer(1.1*p.width)

        #Merge all
        merge = draw.union(horizontal, vertical, circle)


        #Adding cpw lines
        cpw1 = draw.shapely.geometry.LineString([[(cte+2*p.finger_length)/2+p.cap_to_cpw,0],[(cte+2*p.finger_length)/2+p.cap_to_cpw+p.cpw_length,0]])
        cpw2 = cpw1
        cpw3 = cpw1
        cpw4 = cpw1
        cpw2 = draw.rotate(cpw2,90,origin=(0,0))
        cpw3 = draw.rotate(cpw3,180,origin=(0,0))
        cpw4 = draw.rotate(cpw4,-90,origin=(0,0))

        # making the gap to ground of the capacitor
        gap1 = draw.rectangle(cte+2*p.finger_length+2*p.cap_to_cpw+2*p.cpw_length+2*p.gap_to_gnd, p.width+2*p.gap_to_gnd,0,0)
        gap2 = gap1
        gap2 = draw.rotate(gap2, 90)
        gap_circle = draw.shapely.geometry.Point(0,0).buffer(1.1*p.width+2*p.gap_to_gnd)

        merge_gap = draw.union(gap1, gap2, gap_circle)

        # Rotating and translating
        geom_list = [merge, merge_gap, cpw1, cpw2, cpw3, cpw4]
        geom_list = draw.rotate(geom_list, p.orientation, origin=(0,0))
        geom_list = draw.translate(geom_list, p.pos_x, p.pos_y)
        [merge, merge_gap, cpw1, cpw2, cpw3, cpw4] = geom_list

        self.add_qgeometry('poly', {'cap':merge}, layer=p.layer)
        self.add_qgeometry('poly', {'cap_etch':merge_gap}, layer=p.layer, subtract=True)
        self.add_qgeometry('path', {'cpw1':cpw1, 'cpw2':cpw2, 'cpw3':cpw3, 'cpw4':cpw4}, layer=p.layer, width = p.width)
        self.add_qgeometry('path', {'cpw1_etch':cpw1, 'cpw2_etch':cpw2, 'cpw3_etch':cpw3, 'cpw4_etch':cpw4}, layer=p.layer, width = p.width+2*p.gap_to_gnd, subtract=True)

        self.add_pin('pin_1', cpw1.coords, width = p.width, gap = p.gap_to_gnd, input_as_norm=True)
        self.add_pin('pin_2', cpw2.coords, width = p.width, gap = p.gap_to_gnd, input_as_norm=True)
        self.add_pin('pin_3', cpw3.coords, width = p.width, gap = p.gap_to_gnd, input_as_norm=True)
        self.add_pin('pin_4', cpw4.coords, width = p.width, gap = p.gap_to_gnd, input_as_norm=True)