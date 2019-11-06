import tensorflow as tf


def color_area(tf_image_original, color_to_detect, epsilon):
    tf_boolean_channels = []

    for i in range(len(color_to_detect)):
        tf_ = tf.where(((tf_image_original[:, :, i] < (color_to_detect[i] + epsilon)) &
                        (tf_image_original[:, :, i] > (color_to_detect[i] - epsilon))),
                       tf.ones_like(tf_image_original[:, :, i]),
                       tf.zeros_like(tf_image_original[:, :, i]))

        tf_boolean_channels.append(tf.expand_dims(tf_, axis=0, name=None))

    tf_sum = tf.math.reduce_sum(tf.concat(tf_boolean_channels, 0), 0)

    return tf.where(tf_sum >= 3, tf.zeros_like(tf_sum), tf.ones_like(tf_sum))


def bounding_shape_in_box(tf_binary_mask, nb_pixel_min):
    min_axis = []
    max_axis = []

    for i in range(2):
        threshold = tf_binary_mask.shape[i] - nb_pixel_min
        tf_sum_axisi = tf.math.reduce_sum(tf_binary_mask, axis=i)
        min_ = tf.math.reduce_min(tf.where(tf_sum_axisi <= int(threshold)))
        max_ = tf.math.reduce_max(tf.where(tf_sum_axisi <= int(threshold)))
        min_axis.append(min_ / tf_binary_mask.shape[(1 - i) ** 2])
        max_axis.append(max_ / tf_binary_mask.shape[(1 - i) ** 2])

    box = [min_axis[1], min_axis[0], max_axis[1], max_axis[0]]
    box = tf.expand_dims(tf.expand_dims(box, 0), 0)

    return tf.dtypes.cast(box, dtype=tf.float32)


def bounding_color_area(tf_image, color_to_detect, epsilon, nb_pixel_min):
    # Create a detection mask
    tf_color_area = color_area(tf_image, color_to_detect, epsilon)

    # Create the bounding box
    return bounding_shape_in_box(tf_color_area, nb_pixel_min)
