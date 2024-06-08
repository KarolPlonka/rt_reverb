#include <stdbool.h>
#include <stdlib.h>

#define _USE_MATH_DEFINES

// ORIENTATIONS
#define HORIZONTAL 0
#define VERTICAL 1

// DIRECTIONS
#define RIGHT 1 //x
#define LEFT 0 //x
#define UP 1 //y
#define DOWN 0 //y

typedef struct {
    int x;
    int y;
} Point;


typedef struct {
    float value;

    int direction_x;
    int direction_y;
} Slope;


typedef struct {
    Point start_point;
    Point end_point;

    int orientation; //HORIZONTAL, VERTICAL

    Slope* reflection_slopes;
} LineSegment;


typedef struct Ray {
    Point origin_point;

    float slope;
    float y_intercept;

    int direction_x;
    int direction_y;

    float distance_traveled;
    int reflections_count;

    float energy;

    struct Ray* parent;
} Ray;



void throw_error(char* message);

void swap_points(Point* p1, Point* p2);

bool are_same_point(Point* point_1_ptr, Point* point_2_ptr);

float get_distance_squared(Point* point_1_ptr, Point* point_2_ptr);

float get_distance(Point* point_1_ptr, Point* point_2_ptr);

bool validate_wall(LineSegment* line_segment);

bool can_intersect(Ray* ray_ptr, LineSegment* wall_ptr);

Point* get_intersection(Ray* ray_ptr, LineSegment* wall_ptr);

float angle_to_slope(int angle);

bool can_walls_intersect(LineSegment* line_segment_1, LineSegment* line_segment_2);

float get_y_intercept(Point* point_ptr, float slope);

void get_slope_and_y_intercept(Point* point_1_ptr, Point* point_2_ptr, float* slope, float* y_intercept);

Point* get_walls_intersection(LineSegment* line_segment_1, LineSegment* line_segment_2);


