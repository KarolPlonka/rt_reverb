#include "geometry.h"

#include <stdlib.h>
#include <stdio.h>
#include <math.h>


void throw_error(char* message) {
    fprintf(stderr, "%s\n", message);
    exit(EXIT_FAILURE);
}


void swap_points(Point* point_1, Point* point_2) {
    Point temp = *point_1;
    *point_1 = *point_2;
    *point_2 = temp;
}

bool are_same_point(Point* point_1_ptr, Point* point_2_ptr) {
    if (point_1_ptr->x == point_2_ptr->x &&
        point_1_ptr->y == point_2_ptr->y)
    {
        return true;
    }

    return false;
}

float get_distance_squared(Point* point_1_ptr, Point* point_2_ptr) {
    return pow(point_1_ptr->x - point_2_ptr->x, 2) + pow(point_1_ptr->y - point_2_ptr->y, 2);
}


float get_distance(Point* point_1_ptr, Point* point_2_ptr) {
    return sqrt(get_distance_squared(point_1_ptr, point_2_ptr));
}


bool validate_wall(LineSegment* line_segment) {
    if (line_segment->orientation == HORIZONTAL) {
        if (line_segment->start_point.y != line_segment->end_point.y) {
            return false;
        }
        if (line_segment->start_point.x > line_segment->end_point.x) {
            swap_points(&line_segment->start_point, &line_segment->end_point);
        }
    }
    else if (line_segment->orientation == VERTICAL) {
        if (line_segment->start_point.x != line_segment->end_point.x) {
            return false;
        }
        if (line_segment->start_point.y > line_segment->end_point.y) {
            swap_points(&line_segment->start_point, &line_segment->end_point);
        }
    }
    else {
        throw_error("Unhandleable line_segment orientation");
    }

    return true;
}


float angle_to_slope(int angle) {
    return tan(angle * M_PI / 180);
}


bool can_intersect(Ray* ray_ptr, LineSegment* wall_ptr) {
    if (wall_ptr->orientation == HORIZONTAL && wall_ptr->start_point.y == ray_ptr->origin_point.y) {
        return false;
    }

    if (wall_ptr->orientation == VERTICAL && wall_ptr->start_point.x == ray_ptr->origin_point.x) {
        return false;
    }

    if (wall_ptr->orientation == HORIZONTAL) {
        if ((ray_ptr->direction_y == UP   && ray_ptr->origin_point.y > wall_ptr->start_point.y) ||
            (ray_ptr->direction_y == DOWN && ray_ptr->origin_point.y < wall_ptr->start_point.y))
        {
            return false; 
        }
    }
    else if (wall_ptr->orientation == VERTICAL) {
        if ((ray_ptr->direction_x == RIGHT && ray_ptr->origin_point.x > wall_ptr->start_point.x) ||
            (ray_ptr->direction_x == LEFT  && ray_ptr->origin_point.x < wall_ptr->start_point.x))
        {   
            return false;
        }
    }
    
    return true;
}


Point* get_intersection(Ray* ray_ptr, LineSegment* wall_ptr) {
    int intersection_x, intersection_y;

    if (!can_intersect(ray_ptr, wall_ptr)) {
        return NULL;
    }

    if (wall_ptr->orientation == HORIZONTAL) {
        intersection_x = (wall_ptr->start_point.y - ray_ptr->y_intercept) / ray_ptr->slope;
        intersection_y = wall_ptr->start_point.y;

        if (intersection_x < wall_ptr->start_point.x || intersection_x > wall_ptr->end_point.x) {
            return NULL;
        }
    }
    else if (wall_ptr->orientation == VERTICAL) {
        intersection_x = wall_ptr->start_point.x;
        intersection_y = ray_ptr->slope * wall_ptr->start_point.x + ray_ptr->y_intercept;

        if (intersection_y < wall_ptr->start_point.y || intersection_y > wall_ptr->end_point.y) {
            return NULL;
        }
    }

    Point* intersection = malloc(sizeof(Point));
    intersection->x = intersection_x;
    intersection->y = intersection_y;

    return intersection;
}


bool can_walls_intersect(LineSegment* line_segment_1, LineSegment* line_segment_2){
    return (line_segment_1->orientation != line_segment_2->orientation);
}


float get_y_intercept(Point* point_ptr, float slope){
    return point_ptr->y - (slope * point_ptr->x);
}


void get_slope_and_y_intercept(Point* point_1_ptr, Point* point_2_ptr, float* slope, float* y_intercept){
    if (point_1_ptr->x == point_2_ptr->x) {
        *slope = INFINITY;
        *y_intercept = INFINITY;
        return;
    }
    
    if (point_1_ptr->y == point_2_ptr->y) {
        *slope = 0;
        *y_intercept = point_1_ptr->y;
        return;
    }

    *slope = (float) (point_2_ptr->y - point_1_ptr->y) / (point_2_ptr->x - point_1_ptr->x);
    *y_intercept = (float) point_1_ptr->y - (*slope * point_1_ptr->x);
}


Point* get_walls_intersection(LineSegment* line_segment_1, LineSegment* line_segment_2){
    if (!can_walls_intersect(line_segment_1, line_segment_2)) {
        return NULL;
    }

    float intersection_x, intersection_y;

    if (line_segment_1->orientation == HORIZONTAL && line_segment_2->orientation == VERTICAL) {
        intersection_x = line_segment_2->start_point.x;
        intersection_y = line_segment_1->start_point.y;

        if (intersection_x < line_segment_1->start_point.x || intersection_x > line_segment_1->end_point.x ||
            intersection_y < line_segment_2->start_point.y || intersection_y > line_segment_2->end_point.y)
        {
            return NULL;
        }
    }
    else if (line_segment_1->orientation == VERTICAL && line_segment_2->orientation == HORIZONTAL) {
        intersection_x = line_segment_1->start_point.x;
        intersection_y = line_segment_2->start_point.y;

        if (intersection_x < line_segment_2->start_point.x || intersection_x > line_segment_2->end_point.x ||
            intersection_y < line_segment_1->start_point.y || intersection_y > line_segment_1->end_point.y)
        {
            return NULL;
        }
    }
    else {
        throw_error("Unhandleable line_segment orientation");
    }

    Point* intersection = malloc(sizeof(Point));
    intersection->x = intersection_x;
    intersection->y = intersection_y;

    return intersection;
}