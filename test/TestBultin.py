
import unittest
import os.path
import sys

path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(path)

import core
import builtin
import os
import imageio
import numpy as np

test_image = imageio.imread('imageio:chelsea.png')

class BultinImageTest(unittest.TestCase):
    TMP_IMAGE_FILENAME = '.test_chelsea.png'
    TestImage = test_image
    @classmethod
    def setUpClass(cls):
        imageio.imsave(cls.TMP_IMAGE_FILENAME, test_image)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.TMP_IMAGE_FILENAME):
            os.remove(cls.TMP_IMAGE_FILENAME)

    def test_read_image(self):
        reader = builtin.nameless.ImageReader()
        img = reader.read(BultinImageTest.TMP_IMAGE_FILENAME)
        self.assertTrue(img.shape == BultinImageTest.TestImage.shape)
        self.assertTrue(np.all(img == BultinImageTest.TestImage))
    
    def test_write_image(self):
        test_image_path = '.tmp_image.png'
        writer = builtin.nameless.ImageWriter()
        writer.write(test_image_path, BultinImageTest.TestImage)
        img = builtin.nameless.ImageReader().read(test_image_path)
        
        self.assertTrue(np.all(img == BultinImageTest.TestImage))
        
        os.remove(test_image_path)

    def test_as(self):
        app = core.Application()
        func = builtin.nameless.AsVariable()
        app.Variables.push(builtin.nameless.ImageReader().read(BultinImageTest.TMP_IMAGE_FILENAME))
        func.apply('@name', '@temp', -1)
        self.assertTrue('@name' in func.app.Variables)
        self.assertTrue('@temp' not in func.app.Variables)
    
    def test_using(self):
        # This test Will be implemented if other module will have been implemented. 
        #func = builtin.nameless.UsingModule()
        pass


if __name__ == '__main__':
    unittest.main()
