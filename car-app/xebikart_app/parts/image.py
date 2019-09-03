class ImageTransformation:
    def __init__(self, transformations_fn):
        self.transformations_fn = transformations_fn

    def run(self, img_arr):
        for transformation_fn in self.transformations_fn:
            img_arr = transformation_fn(img_arr)
        return img_arr
