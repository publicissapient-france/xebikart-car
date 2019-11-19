import tensorflow as tf


def color_area(tf_image_original, color_to_detect, epsilon):
    tf_boolean_channels = []

    for i in range(len(color_to_detect)):
        tf_ = tf.where(((tf_image_original[:, :, i] < (color_to_detect[i] + epsilon[i])) &
                        (tf_image_original[:, :, i] > (color_to_detect[i] - epsilon[i]))),
                       tf.ones_like(tf_image_original[:, :, i]),
                       tf.zeros_like(tf_image_original[:, :, i]))

        tf_boolean_channels.append(tf.expand_dims(tf_, axis=0, name=None))

    tf_sum = tf.math.reduce_sum(tf.concat(tf_boolean_channels, 0), 0)

    return tf.where(tf_sum >= 3, tf.zeros_like(tf_sum), tf.ones_like(tf_sum))


def bounding_shape_in_box(tf_binary_mask, nb_pixel_min):
    x_threshold = tf_binary_mask.shape[0] - nb_pixel_min
    x_sum_axis = tf.math.reduce_sum(tf_binary_mask, axis=0)
    x_min = tf.math.reduce_min(tf.where(x_sum_axis <= int(x_threshold)))
    x_max = tf.math.reduce_max(tf.where(x_sum_axis <= int(x_threshold)))

    y_threshold = tf_binary_mask.shape[1] - nb_pixel_min
    y_sum_axis = tf.math.reduce_sum(tf_binary_mask, axis=1)
    y_min = tf.math.reduce_min(tf.where(y_sum_axis <= int(y_threshold)))
    y_max = tf.math.reduce_max(tf.where(y_sum_axis <= int(y_threshold)))

    return [y_min.numpy().item(), x_min.numpy().item(), y_max.numpy().item(), x_max.numpy().item()]


def bounding_color_area_in_box(tf_image, color_to_detect, epsilon, nb_pixel_min):
    # Create a detection mask
    tf_color_area = color_area(tf_image, color_to_detect, epsilon)

    # Create the bounding box
    return bounding_shape_in_box(tf_color_area, nb_pixel_min)
