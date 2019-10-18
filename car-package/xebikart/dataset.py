import pathlib

import pandas as pd
import tensorflow as tf

from donkeycar.parts.datastore import Tub


def _get_archive(tubes_root_path, tube_name, tubes_extension, cache_dir):
    tube_name_extension = f"{tube_name}{tubes_extension}"
    path = tf.keras.utils.get_file(tube_name_extension, f"{tubes_root_path}/{tube_name_extension}",
                                   cache_dir=cache_dir, extract=True)
    path = path[:-len(tubes_extension)]
    return pathlib.Path(path)


def get_tubes_df(tubes_root_path, tubes_name, tubes_extension="", cache_dir=None):
    tubes = []
    i = 0
    # get files
    for tube_name in tubes_name:
        path = _get_archive(tubes_root_path, tube_name, tubes_extension, cache_dir)
        tub = Tub(str(path))
        tub_df = tub.get_df()
        tub_df["num_tube"] = i # track the different tubes
        tubes.append(tub_df)
        i += 1

    return pd.concat(tubes, sort=False)


def _find_tubes(data_root):
    tubes_path = []

    tubes_path += list(data_root.glob('*.jpg'))
    if len(tubes_path) == 0:
        print("No image (.jpg) in %s" % str(data_root))

    return tubes_path


def get_tubes(tubes_root_path, tubes_name, tubes_extension="", cache_dir=None):
    tubes_path = []

    # get files
    for tube_name in tubes_name:
        path = _get_archive(tubes_root_path, tube_name, tubes_extension, cache_dir)
        tubes_path.extend(_find_tubes(path))
    tubes_path = [str(tub_path) for tub_path in tubes_path]
    return tubes_path
