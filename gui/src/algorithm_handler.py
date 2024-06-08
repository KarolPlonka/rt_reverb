from ctypes import *

from time import perf_counter
import pandas as pd

class Point(Structure):
    _fields_ = [
        ("x", c_int),
        ("y", c_int),
    ]


class Listener(Structure):
    _fields_ = [
        ("left_channel_point", Point),
        ("right_channel_point", Point),
    ]


class Sound_Source(Structure):
    _fields_ = [
        ("point", Point),
        ("direction_angle", c_int),
    ]


class Rectangular_Wall_Scheme(Structure):
    _fields_ = [
        ("bottom_left", Point),
        ("top_right", Point),
        ("reflectivity", c_float),
        ("speed_of_sound_cm_per_sec", c_float),
    ]


Callback_Function = CFUNCTYPE(
    None, # return type
    c_float, # time in seconds
    c_float, # energy
    POINTER(Point), # path
    c_int, # points amount
    c_bool, # are obstacles on path
    c_int, # channel id
)



class AlgorithmHandler:

    class BakingException(Exception):
        pass

    def __init__(self):
        self.lib = CDLL('../../algorithm/build/libRayTracing.dll')
        # self.lib = CDLL('libRayTracing.dll') # Realse

        self.c_function_run_simulation = self.lib.run_ray_tracing

        self.c_function_run_simulation.argtypes = [
            c_int, # scene width
            c_int, # scene height
            c_float, # scene walls reflectivity               
            Sound_Source, # sound source
            Listener, # listener
            POINTER(Rectangular_Wall_Scheme), # 2D array of points (rectangular walls)
            c_int, # number of rectangular walls
            c_int, # reflections amount
            c_int, # initial rays amount
            c_float, # minimal energy threshold
            Callback_Function, # callback function
        ]


    def get_walls_schemes(self, rectangular_walls):
        rectangular_walls_schemes = [
            Rectangular_Wall_Scheme(
                self.get_c_point(wall.get_bottom_left_point()),
                self.get_c_point(wall.get_top_right_point()),
                wall.get_reflectivity(),
                wall.get_speed_of_sound_cm_per_sec(),
            )
            for wall in rectangular_walls
        ]

        return (Rectangular_Wall_Scheme * len(rectangular_walls_schemes))(*rectangular_walls_schemes)
    

    def run_simulation(
        self,
        scene_width,
        scene_height,
        scene_walls_reflectivity,
        rectangular_walls,
        sound_source,
        listener,
        reflections_amount,
        inital_rays_amount,
        min_energy_threshold,
        caught_ray_callback
    ):
        listener = Listener(
            self.get_c_point(listener.get_left_channel_point()),
            self.get_c_point(listener.get_right_channel_point()),
        )

        sound_source = Sound_Source(
            self.get_c_point(sound_source.get_center()),
            sound_source.get_vertically_flipped_direction_angle(),
        )

        rectangular_walls_schemes = self.get_walls_schemes(rectangular_walls)

        try:
            start_time = perf_counter()
            self.c_function_run_simulation(
                scene_width,
                scene_height,
                scene_walls_reflectivity,
                sound_source,
                listener,
                rectangular_walls_schemes,
                len(rectangular_walls),
                reflections_amount,
                inital_rays_amount,
                min_energy_threshold,
                Callback_Function(caught_ray_callback),
            )
            total_time = perf_counter() - start_time



        except Exception as e:
            raise self.BakingException(e)


    def get_c_point(self, coords):
        return Point( int(coords[0]), int(coords[1]))

    
    # def test(self):
    #     sound_source = Point(1, 2, False)
    #     listener = Circle(Point(3, 4, False), 20)

    #     points_data = [
    #         [Point(1, 2, True), Point(3, 4, False)],
    #         [Point(3, 4, False), Point(5, 6, True)],
    #         [Point(7, 8, False), Point(9, 10, True)]
    #     ]

    #     # Create a C-compatible 2D array of Point structs
    #     num_rows = len(points_data)
    #     num_cols = len(points_data[0])

    #     # Create a temporary array to hold the pointers to Point structs
    #     point_rows = []
    #     for row in points_data:
    #         point_row = (Point * num_cols)(*row)
    #         point_rows.append(point_row)

    #     # Create a 2D array of Point structs
    #     points = (POINTER(Point) * num_rows)(*point_rows)

    #     self.c_function_run_simulation(
    #         40,
    #         80,
    #         sound_source,
    #         listener,
    #         points,
    #         3
    #     )

