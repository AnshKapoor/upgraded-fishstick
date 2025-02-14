import unittest
import random
import os
from gseos_qt.utils.plugin_settings import PluginSettings


class TestPluginSettings(unittest.TestCase):
    def setUp(self):
        self.s = self.plugin_settings = PluginSettings(__file__)
        if os.path.isfile(self.s.json):
            os.remove(self.s.json)
        self.data = list()
        self.keys = list()

    def tearDown(self):
        if os.path.isfile(self.s.json):
            with open(self.s.json, "r") as f:
                print(f.read())
            os.remove(self.s.json)
        else:
            print("NOT WRITTEN")
            print(self.s.data)

    def test_1(self):
        """ Testing writing of default values """

        for i in range(10):
            n = random.randint(1, 100)
            while n in self.keys:
                n = random.randint(1, 100)
            m = random.randint(1, 100)
            self.data.append((n, m))
            self.keys.append(n)
            self.assertEqual(self.s.get(n, m), m)

    def test_2(self):
        """ Testing writing of default values (nested) """

        for i in range(10):
            n = random.randint(1, 100)
            while n in self.keys:
                n = random.randint(1, 100)
            m = random.randint(1, 100)
            self.data.append((["l1", "l2", n], m))
            self.keys.append(n)
            self.assertEqual(self.s.get(["l1", "l2", n], m), m)

    def test_3(self):
        """ Testing reading of written values """

        self.data = list()
        self.keys = list()
        self.test_1()
        self.test_2()
        for n, m in self.data:
            self.assertEqual(self.s.get(n, None), m)

        import time
        time.sleep(.5)


if __name__ == '__main__':
    unittest.main()
