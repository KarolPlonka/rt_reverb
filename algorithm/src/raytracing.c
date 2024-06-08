#include "raytracing.h"

#define ENERGY_LOSS_COEFFICIENT 1

#define SPEED_OF_SOUND_IN_AIR_CM_PER_SEC 34300

#define MAX_DISTANCE INFINITY

int REFLECTIONS_COUNT; //remove later

Callback_Function external_register_caught_ray;

Point* get_ray_path(Ray* ray_ptr, Point* listener_point_ptr, int path_lenght) {
    Point* path = malloc(sizeof(Point) * path_lenght);

    path[0] = *listener_point_ptr;

    for (int i = 1; i < path_lenght; i++) {
        path[i] = ray_ptr->origin_point;
        ray_ptr = ray_ptr->parent;
    }

    return path;
}


Obstacle* get_obstacle_ptr(Point* ray_origin_point_ptr, Intersection* intersections, size_t intersections_count) {
    Obstacle* obstacle_ptr = malloc(sizeof(Obstacle));

    if (intersections_count == 1) {
        obstacle_ptr->entry_point_ptr = intersections[0].point_ptr;
        obstacle_ptr->exit_point_ptr = intersections[0].point_ptr;
        obstacle_ptr->entry_point_wall_ptr = intersections[0].wall_ptr;
        obstacle_ptr->distance_to_entry_point_squared = intersections[0].distance_squared;

        return obstacle_ptr;
    }
    
    if (intersections_count == 2) {

        if (intersections[0].distance_squared < intersections[1].distance_squared) {
            obstacle_ptr->entry_point_ptr = intersections[0].point_ptr;
            obstacle_ptr->exit_point_ptr = intersections[1].point_ptr;
            obstacle_ptr->entry_point_wall_ptr = intersections[0].wall_ptr;
            obstacle_ptr->distance_to_entry_point_squared = intersections[0].distance_squared;
        }
        else {
            obstacle_ptr->entry_point_ptr = intersections[1].point_ptr;
            obstacle_ptr->exit_point_ptr = intersections[0].point_ptr;
            obstacle_ptr->entry_point_wall_ptr = intersections[1].wall_ptr;
            obstacle_ptr->distance_to_entry_point_squared = intersections[1].distance_squared;
        }

        return obstacle_ptr;
    }

    printf("Error: more than 2 intersections with rectangular wall!");
    exit(EXIT_FAILURE);
}


Obstacle* get_intersection_with_rectangular_wall(Ray* ray_ptr, Rectangular_Wall* r_wall_ptr) {
    Intersection intersections[2];
    size_t intersections_count = 0;

    for (int l_wall_id = 0; l_wall_id < 4; l_wall_id++) {
        Point* intersection_point_ptr = get_intersection(
            ray_ptr,
            r_wall_ptr->line_segments[l_wall_id]
        );

        if (intersection_point_ptr == NULL) {
            continue;
        }

        Intersection intersection = {
            .point_ptr = intersection_point_ptr,
            .wall_ptr = r_wall_ptr->line_segments[l_wall_id],
            .distance_squared = get_distance_squared(
                &ray_ptr->origin_point,
                intersection_point_ptr
            ),
        };

        if (intersections_count < 2){
            intersections[intersections_count++] = intersection;
            continue;
        }

        if (intersections_count == 2) {
            int orientation = r_wall_ptr->line_segments[l_wall_id]->orientation;

            if (orientation == intersections[0].wall_ptr->orientation) {
                intersections[1] = intersection;
                continue;
            }

            if (orientation == intersections[1].wall_ptr->orientation) {
                intersections[0] = intersection;
                continue;
            }
        }
    }

    if (intersections_count == 0) {
        return NULL;
    }

    Obstacle* obstacle_ptr = get_obstacle_ptr(&ray_ptr->origin_point, intersections, intersections_count);
    obstacle_ptr->rectangular_wall_ptr = r_wall_ptr;

    return obstacle_ptr;
}


Obstacle* get_obstacles_in_path(Ray* ray_ptr, Scene* scene_ptr, size_t* obstacles_count_ptr, bool skip_boundaries){
    size_t max_obstacles_amount = scene_ptr->rectangular_walls_amount - (skip_boundaries ? 1 : 0);
    Obstacle* obstacles = malloc(sizeof(Obstacle) * max_obstacles_amount);

    *obstacles_count_ptr = 0;

    for (int r_wall_id = 0; r_wall_id < scene_ptr->rectangular_walls_amount; r_wall_id++) {
        if (skip_boundaries && scene_ptr->rectangular_walls[r_wall_id].is_boundary) {
            continue;
        }

        Obstacle* obstacle_ptr = get_intersection_with_rectangular_wall(ray_ptr, &(scene_ptr->rectangular_walls[r_wall_id]));

        if (obstacle_ptr != NULL) {
            obstacles[(*obstacles_count_ptr)++] = *obstacle_ptr;
        }
    }

    obstacles = realloc(obstacles, sizeof(Obstacle) * (*obstacles_count_ptr));

    return obstacles;
}


Obstacle* get_closest_obstacle(Ray* ray_ptr, Scene* scene_ptr){
    size_t obstacles_amount = 0;
    Obstacle* obstacles = get_obstacles_in_path(ray_ptr, scene_ptr, &obstacles_amount, false);

    if (obstacles_amount == 0) {
        return NULL;
    }
 
    Obstacle* closest_obstacle_ptr = &obstacles[0];

    for (int i = 1; i < obstacles_amount; i++) {
        if (obstacles[i].distance_to_entry_point_squared < closest_obstacle_ptr->distance_to_entry_point_squared) {
            closest_obstacle_ptr = &obstacles[i];
        }
    }

    return closest_obstacle_ptr;
}


bool is_corner(Point* point, Point* corners, int corners_count) {
    for (int i = 0; i < corners_count; i++) {
        if (are_same_point(point, &corners[i])) {
            return true;
        }
    }
    return false;
}


float get_time(float distance_cm, float speed_of_sound_cm_per_sec) {
    return distance_cm / speed_of_sound_cm_per_sec;
}


float get_energy_reduction(float absorption, float distance_in_obstacle_m){
    return exp(-distance_in_obstacle_m * ENERGY_LOSS_COEFFICIENT * absorption);
}


Ray get_ray_to_point(Point* origin_point_ptr, Point* target_point_ptr, Ray* parent_ray_ptr){
    float slope, y_intercept;
    get_slope_and_y_intercept(origin_point_ptr, target_point_ptr, &slope, &y_intercept);

    float distance_traveled = get_distance(origin_point_ptr, target_point_ptr);
    int reflections_count = 1;
    float energy = 1.0f;
    Ray* parent = NULL;

    if (parent_ray_ptr != NULL){
        distance_traveled += parent_ray_ptr->distance_traveled;
        reflections_count += parent_ray_ptr->reflections_count;
        energy = parent_ray_ptr->energy;
        parent = parent_ray_ptr;
    }

    return (Ray) {
        .origin_point = *origin_point_ptr,
        .slope = slope,
        .y_intercept = y_intercept,
        .direction_x = (origin_point_ptr->x < target_point_ptr->x) ? RIGHT : LEFT,
        .direction_y = (origin_point_ptr->y < target_point_ptr->y) ? UP : DOWN,
        .distance_traveled = distance_traveled,
        .reflections_count = reflections_count,
        .energy = energy,
        .parent = parent,
    };
}


void connect_ray_to_channel_point(Ray* ray_ptr, size_t channel_id, Scene* scene_ptr) {
    Point* channel_point_ptr = &scene_ptr->listener.channels_points[channel_id];

    size_t obstacles_amount = 0;

    Obstacle* obstacles = get_obstacles_in_path(ray_ptr, scene_ptr, &obstacles_amount, true); 

    float distance_to_listener = get_distance(&ray_ptr->origin_point, channel_point_ptr);
    float distance_in_obstacles = 0;
    float time_in_obstacles = 0;

    float energy = ray_ptr->energy;

    Point* previous_point_ptr = &ray_ptr->origin_point;

    for (int i = 0; i < obstacles_amount; i++){
        if(obstacles[i].distance_to_entry_point_squared > pow(distance_to_listener, 2)){
            continue;
        }

        float distance_in_obstacle = get_distance(
            obstacles[i].entry_point_ptr,
            obstacles[i].exit_point_ptr
        );

        time_in_obstacles += get_time(
            distance_in_obstacle,
            obstacles[i].rectangular_wall_ptr->speed_of_sound_cm_per_sec
        );

        distance_in_obstacles += distance_in_obstacle;

        energy *= get_energy_reduction(
            1.f - obstacles[i].rectangular_wall_ptr->reflectivity,
            distance_in_obstacle / 100
        );
        energy *= 1.f - obstacles[i].rectangular_wall_ptr->reflectivity;
    }

    float distance_in_air = distance_to_listener - distance_in_obstacles;

    float time_in_air = get_time(distance_in_air, SPEED_OF_SOUND_IN_AIR_CM_PER_SEC);

    add_caught_ray(scene_ptr, *ray_ptr);

    int path_length = ray_ptr->reflections_count + 1;

    Point* path = get_ray_path(ray_ptr, channel_point_ptr, path_length);

    bool are_obstacles_on_path = obstacles_amount > 0;

    external_register_caught_ray(
        time_in_air + time_in_obstacles, 
        energy,
        path,
        path_length,
        are_obstacles_on_path,
        channel_id
    );
}


void connect_to_listener(Point* connect_from_point_ptr, Scene* scene_ptr, Ray* parent_ray_ptr) {
    for (int channel_id = 0; channel_id < 2; channel_id++){
        Ray ray_to_channel = get_ray_to_point(
            connect_from_point_ptr,
            &scene_ptr->listener.channels_points[channel_id],
            parent_ray_ptr
        );

        connect_ray_to_channel_point(
            &ray_to_channel,
            channel_id,
            scene_ptr
        );
    }
}


void cast(Ray parent_ray, Scene* scene_ptr, Settings* settings_ptr) {
    if (parent_ray.energy < settings_ptr->min_energy_threshold) {
        return;
    }

    REFLECTIONS_COUNT++;

    Obstacle* obstacle_ptr = get_closest_obstacle(&parent_ray, scene_ptr);
    if (obstacle_ptr == NULL) {
        printf("Warnning: stray ray!\n");
        return;
    }

    if ( is_corner(obstacle_ptr->entry_point_ptr, scene_ptr->corners, scene_ptr->corners_amount) ) {
        return;
    }
    
    parent_ray.energy *= obstacle_ptr->rectangular_wall_ptr->reflectivity;

    connect_to_listener(obstacle_ptr->entry_point_ptr, scene_ptr, &parent_ray);

    Slope* reflections_slopes = obstacle_ptr->entry_point_wall_ptr->reflection_slopes;


    float child_ray_distance_traveled = parent_ray.distance_traveled + sqrt(obstacle_ptr->distance_to_entry_point_squared);

    float child_ray_energy = parent_ray.energy / settings_ptr->reflections_amount;

    for (int i = 0; i < settings_ptr->reflections_amount; i++){
        if (parent_ray.slope == reflections_slopes[i].value) {
            continue;
        }

        Ray child_ray = {
            .origin_point = *obstacle_ptr->entry_point_ptr,
            .slope = reflections_slopes[i].value,
            .y_intercept = get_y_intercept(obstacle_ptr->entry_point_ptr, reflections_slopes[i].value),
            .direction_x = reflections_slopes[i].direction_x, 
            .direction_y = reflections_slopes[i].direction_y,
            .distance_traveled = child_ray_distance_traveled,
            .reflections_count = parent_ray.reflections_count + 1,
            .energy = child_ray_energy,
            .parent = &parent_ray,
        }; 

        cast(child_ray, scene_ptr, settings_ptr);
    }      
}          
           

Ray* execute_simulation(Scene* scene_ptr, Settings* settings_ptr){
    // PREPARE
    REFLECTIONS_COUNT = 0;

    for (int rectangular_wall_id = 0; rectangular_wall_id < scene_ptr->rectangular_walls_amount; rectangular_wall_id++) {
        for (int linear_wall_id = 0; linear_wall_id < 4; linear_wall_id++) {
            validate_wall(scene_ptr->rectangular_walls[rectangular_wall_id].line_segments[linear_wall_id]);
        }
    }

    find_corners(scene_ptr);

    // RUN
    connect_to_listener(&scene_ptr->sound_source.point, scene_ptr, NULL);

    int step = 180 / settings_ptr->initial_rays_amount;
    int start_angle = scene_ptr->sound_source.direction_angle - 90 + (step / 2);
    int end_angle = scene_ptr->sound_source.direction_angle + 90;


    for (int angle = start_angle; angle < end_angle; angle += step) {
        int normalized_angle = angle % 360;
        float slope = angle_to_slope(normalized_angle);

        Ray initial_ray = {
            .origin_point = scene_ptr->sound_source.point,
            .slope = slope,
            .y_intercept = get_y_intercept(&scene_ptr->sound_source.point, slope),
            .direction_x = (normalized_angle > 90 && normalized_angle < 270) ? LEFT : RIGHT,
            .direction_y = (normalized_angle > 0 && normalized_angle < 180) ? UP : DOWN,
            .distance_traveled = 0,
            .reflections_count = 1,
            .energy = 1.0f / settings_ptr->initial_rays_amount,
            .parent = NULL,
        };
        
        cast(initial_ray, scene_ptr, settings_ptr);
    }

    // FINISH 
    printf("REFLECTIONS_COUNT: %d\n", REFLECTIONS_COUNT);
    printf("CAUGHT_RAYS_AMOUNT: %d\n", scene_ptr->caught_rays_amount);

    return scene_ptr->caught_rays;
}


void add_caught_ray(Scene* scene_ptr, Ray ray){
    if(scene_ptr->caught_rays_amount == scene_ptr->caught_rays_capacity){
        scene_ptr->caught_rays_capacity += 20;
        scene_ptr->caught_rays = realloc(scene_ptr->caught_rays, scene_ptr->caught_rays_capacity * sizeof(Ray));
    }

    scene_ptr->caught_rays[scene_ptr->caught_rays_amount++] = ray;
}


void add_corner(Scene *scene_ptr, Point corner){
    if(scene_ptr->corners_amount == scene_ptr->corners_capacity){
        scene_ptr->corners_capacity += 10;
        scene_ptr->corners = realloc(scene_ptr->corners, scene_ptr->corners_capacity * sizeof(Point));
    }

    scene_ptr->corners[scene_ptr->corners_amount++] = corner;
}


void add_scene_boundary_walls(Scene* scene_ptr, int width, int height, float reflectivity, Slope*** reflection_slopes){
    LineSegment* top_wall = malloc(sizeof(LineSegment));
    *top_wall = (LineSegment) {
        .start_point = {0, height},
        .end_point = {width, height},
        .orientation = HORIZONTAL,
        .reflection_slopes = reflection_slopes[HORIZONTAL][DOWN]
    };

    LineSegment* right_wall = malloc(sizeof(LineSegment));
    *right_wall = (LineSegment) {
        .start_point = {width, 0},
        .end_point = {width, height},
        .orientation = VERTICAL,
        .reflection_slopes = reflection_slopes[VERTICAL][LEFT]
    };

    LineSegment* bottom_wall = malloc(sizeof(LineSegment));
    *bottom_wall = (LineSegment) {
        .end_point = {width, 0},
        .orientation = HORIZONTAL,
        .reflection_slopes = reflection_slopes[HORIZONTAL][UP]
    };

    LineSegment* left_wall = malloc(sizeof(LineSegment));
    *left_wall = (LineSegment) {
        .start_point = {0, 0},
        .end_point = {0, height},
        .orientation = VERTICAL,
        .reflection_slopes = reflection_slopes[VERTICAL][RIGHT]
    };

    Rectangular_Wall rWall = {
        .top_wall = top_wall,
        .right_wall = right_wall,
        .bottom_wall = bottom_wall,
        .left_wall = left_wall,
        .reflectivity = reflectivity,
        .is_boundary = true,
    };

    add_corner(scene_ptr, (Point){0, 0});
    add_corner(scene_ptr, (Point){width, 0});
    add_corner(scene_ptr, (Point){width, height});
    add_corner(scene_ptr, (Point){0, height});

    if(scene_ptr->rectangular_walls_amount == scene_ptr->rectangular_walls_capacity){
        scene_ptr->rectangular_walls_capacity += 10;
        scene_ptr->rectangular_walls = realloc(
            scene_ptr->rectangular_walls,
            scene_ptr->rectangular_walls_capacity * sizeof(Rectangular_Wall)
        );
    }

    scene_ptr->rectangular_walls[scene_ptr->rectangular_walls_amount++] = rWall;
}


void add_rectangular_wall(Scene* scene_ptr, Rectangular_Wall_Scheme* scheme, Slope*** reflection_slopes){

    LineSegment* top_wall = malloc(sizeof(LineSegment));
    *top_wall = (LineSegment) {
        .start_point = (Point){scheme->bottom_left.x, scheme->top_right.y},
        .end_point = scheme->top_right,
        .orientation = HORIZONTAL,
        .reflection_slopes = reflection_slopes[HORIZONTAL][UP]
    };

    LineSegment* bottom_wall = malloc(sizeof(LineSegment));
    *bottom_wall = (LineSegment) {
        .start_point = scheme->bottom_left,
        .end_point = (Point){scheme->top_right.x, scheme->bottom_left.y},
        .orientation = HORIZONTAL,
        .reflection_slopes = reflection_slopes[HORIZONTAL][DOWN]
    };

    LineSegment* left_wall = malloc(sizeof(LineSegment));
    *left_wall = (LineSegment) {
        .start_point = scheme->bottom_left,
        .end_point = (Point){scheme->bottom_left.x, scheme->top_right.y},
        .orientation = VERTICAL,
        .reflection_slopes = reflection_slopes[VERTICAL][LEFT]
    };

    LineSegment* right_wall = malloc(sizeof(LineSegment));
    *right_wall = (LineSegment) {
        .start_point = (Point){scheme->top_right.x, scheme->bottom_left.y},
        .end_point = scheme->top_right,
        .orientation = VERTICAL,
        .reflection_slopes = reflection_slopes[VERTICAL][RIGHT]
    };


    Rectangular_Wall rWall = {
        .top_wall = top_wall,
        .right_wall = right_wall,
        .bottom_wall = bottom_wall,
        .left_wall = left_wall,
        
        .reflectivity = scheme->reflectivity,
        .speed_of_sound_cm_per_sec = scheme->speed_of_sound_cm_per_sec,
        .is_boundary = false,
    };


    if(scene_ptr->rectangular_walls_amount == scene_ptr->rectangular_walls_capacity){
        scene_ptr->rectangular_walls_capacity += 10;
        scene_ptr->rectangular_walls = realloc(
            scene_ptr->rectangular_walls,
            scene_ptr->rectangular_walls_capacity * sizeof(Rectangular_Wall)
        );
    }

    scene_ptr->rectangular_walls[scene_ptr->rectangular_walls_amount++] = rWall;
}



void find_corners(Scene* scene_ptr){
    for (int rwall_idx_1 = 0; rwall_idx_1 < scene_ptr->rectangular_walls_amount; rwall_idx_1++) {
        for (int rwall_idx_2 = 1 + rwall_idx_1; rwall_idx_2 < scene_ptr->rectangular_walls_amount; rwall_idx_2++) {
            for (int wall_idx_1 = 0; wall_idx_1 < 4; wall_idx_1++) {
                for (int wall_idx_2 = 0; wall_idx_2 < 4; wall_idx_2++) {

                    Point* intersection = get_walls_intersection(
                        scene_ptr->rectangular_walls[rwall_idx_1].line_segments[wall_idx_1],
                        scene_ptr->rectangular_walls[rwall_idx_2].line_segments[wall_idx_2]
                    );

                    if (intersection != NULL) {
                        scene_ptr->corners[scene_ptr->corners_amount++] = *intersection;
                    }

                }
            }
        }
    }
}

Slope*** get_slopes(int amount) {
    Slope*** reflection_slopes = malloc(2 * sizeof(Slope**));
    for (int i = 0; i < 2; i++) {
        reflection_slopes[i] = malloc(2 * sizeof(Slope*));
        for (int j = 0; j < 2; j++) {
            reflection_slopes[i][j] = malloc(amount * sizeof(Slope));
        }
    }

    int step = 180 / amount;

    for (int i = 0, angle = 0 + (step / 2); i < amount; i++, angle += step) {
        reflection_slopes[HORIZONTAL][UP][i] = (Slope) {
            .value = angle_to_slope(angle),
            .direction_x = (angle < 90) ? RIGHT : LEFT,
            .direction_y = UP
        };
    }

    for (int i = 0, angle = 180 + (step / 2); i < amount; i++, angle += step) {
        reflection_slopes[HORIZONTAL][DOWN][i] = (Slope) {
            .value = angle_to_slope(angle),
            .direction_x = (angle < 270) ? LEFT : RIGHT,
            .direction_y = DOWN
        };
    }

    for (int i = 0, angle = 90 + (step / 2); i < amount; i++, angle += step) {
        reflection_slopes[VERTICAL][LEFT][i] = (Slope) {
            .value = angle_to_slope(angle),
            .direction_x = LEFT,
            .direction_y = (angle < 180) ? UP : DOWN
        };
    }

    for (int i = 0, angle = 270 + (step / 2); i < amount; i++, angle += step) {
        reflection_slopes[VERTICAL][RIGHT][i] = (Slope) {
            .value = angle_to_slope(angle),
            .direction_x = RIGHT,
            .direction_y = (angle < 360) ? DOWN : UP
        };
    }

    return reflection_slopes;
}

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
)
{
    external_register_caught_ray = register_caught_ray;

    Slope*** reflections_slopes = get_slopes(reflections_amount);

    Scene scene = {
        .sound_source = sound_source,

        .listener = listener,

        .caught_rays = NULL,
        .caught_rays_amount = 0,
        .caught_rays_capacity = 0,

        .rectangular_walls = NULL,
        .rectangular_walls_amount = 0,
        .rectangular_walls_capacity = 0,
    };

    Settings settings = {
        .reflections_amount = reflections_amount,
        .initial_rays_amount = initial_rays_amount,
        .min_energy_threshold = min_energy_threshold,
    };

    add_scene_boundary_walls(&scene, scene_width, scene_height, scene_wall_reflectivity, reflections_slopes);

    for (int i = 0; i < rectangular_walls_count; i++) {
        add_rectangular_wall(&scene, &rectangular_walls_schemes[i], reflections_slopes);
    }

    execute_simulation(&scene, &settings);
}
