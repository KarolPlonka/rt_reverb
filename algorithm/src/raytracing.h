#include "geometry/geometry.h"

#include <stdio.h>
#include <stdbool.h>
#include <math.h>


typedef struct {
    Point bottom_left;
    Point top_right;

    float reflectivity;
    float speed_of_sound_cm_per_sec;
} Rectangular_Wall_Scheme;


typedef struct {
    union{
        struct{
            LineSegment* top_wall;
            LineSegment* bottom_wall;
            LineSegment* left_wall;
            LineSegment* right_wall;
        };
        LineSegment* line_segments[4];
    };

    float reflectivity;
    float speed_of_sound_cm_per_sec;
    bool is_boundary;
} Rectangular_Wall;


typedef struct {
    Rectangular_Wall* rectangular_wall_ptr;
    LineSegment* entry_point_wall_ptr;

    Point* entry_point_ptr;
    Point* exit_point_ptr;

    float distance_to_entry_point_squared;
} Obstacle;


typedef struct {
    Point* point_ptr;
    LineSegment* wall_ptr;
    float distance_squared;
} Intersection;


typedef struct {
    Point point;
    int direction_angle;
} Sound_Source;


typedef struct {
    union {
        struct {
            Point left_channel_point;
            Point right_channel_point;
        };
        Point channels_points[2];
    };
} Listener;


typedef struct {
    int reflections_amount;
    int initial_rays_amount;
    float min_energy_threshold;
} Settings;


typedef struct {
    Sound_Source sound_source;
    Listener listener;

    Ray* caught_rays;
    int caught_rays_amount;
    int caught_rays_capacity;

    Rectangular_Wall* rectangular_walls;
    int rectangular_walls_amount;
    int rectangular_walls_capacity;

    Point* corners;
    int corners_amount;
    int corners_capacity;
} Scene;


typedef void (*Callback_Function)(
    float, // time 
    float, // energy
    Point*,// path (array of points) 
    int,   // path length
    bool,  // are_obstacles_on_path
    int    // channel_id (0 - left, 1 - right)
);



void run_ray_tracing(
    int scene_width,
    int scene_height,
    float scene_wall_reflectivity,
    Sound_Source sound_source,
    Listener listener,
    Rectangular_Wall_Scheme* rectangular_walls_schemes,
    int rectangular_walls_count,
    int reflections_amount,
    int initial_rays_amount,
    float min_energy_threshold,
    Callback_Function register_caught_ray
);


bool is_corner(Point* point, Point* corners, int corners_count);

void cast(Ray parent_ray, Scene* scene, Settings* settings);

Ray* execute_simulation(Scene* scene, Settings* settings);

void add_corner(Scene* scene, Point corner);

LineSegment* add_wall(Scene* scene, LineSegment wall);

void add_caught_ray(Scene* scene, Ray ray);

Rectangular_Wall create_rectangular_wall(Scene* scene, Point bottom_left, Point top_right, float reflectivity);

bool validate_wall(LineSegment* wall);

void find_corners(Scene* scene);


