CLIPPING_MARGIN = 10 # px

def is_rectangle_clipping_with_circle(
        rectangle_x1, rectangle_y1, rectangle_x2, rectangle_y2,
        circle_x, circle_y, circle_radius
    ):

    left_x, right_x = sorted([rectangle_x1, rectangle_x2])
    top_y, bottom_y = sorted([rectangle_y1, rectangle_y2])

    if (
        left_x - CLIPPING_MARGIN - circle_radius <= circle_x <= right_x + CLIPPING_MARGIN + circle_radius and
        top_y - CLIPPING_MARGIN - circle_radius <= circle_y <= bottom_y + CLIPPING_MARGIN + circle_radius
    ):
        return True

    return False