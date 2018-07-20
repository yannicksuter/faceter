import unittest
import svg

class TestSVG(unittest.TestCase):
    def test_load_path(self):
        paths = svg.Path.read(f'../example/svg/0123.svg')

if __name__ == '__main__':
    unittest.main()
