import unittest
import GpsNominatim
import Functions


class TestGpsNominatim(unittest.TestCase):
    """[summary]

    Args:
        unittest ([type]): [description]
    """

    def test_get_close(self):
        closest = GpsNominatim.get_close(15, 15)
        self.assertEqual(str, type(closest[0]))
        self.assertEqual(float, type(closest[1]))
        self.assertEqual('52240', closest[0])
        self.assertEqual(4494718.609928241, closest[1])

    def test_distance(self):
        distance = GpsNominatim.distance(15, 15, 13, 13)
        self.assertEqual(float, type(distance))
        self.assertEqual(224459.24417612093, distance)

    def test_get_wind(self):
        data = GpsNominatim.get_wind(97200)
        self.assertEqual(str, type(data))

    def test_get_temp(self):
        data = GpsNominatim.get_wind(97200)
        self.assertEqual(str, type(data))


class TestFunctions(unittest.TestCase):
    """[summary]

    Args:
        unittest ([type]): [description]
    """

    def test_calc_wind(self):
        data = Functions.calc_wind(97200, 3000)
        self.assertEqual(float, type(data))

    def test_calc_station(self):
        data = Functions.calc_station("grondalsvagen 110", "117 69")
        self.assertEqual(tuple, type(data))
        self.assertEqual(str, type(data[0]))
        self.assertEqual(float, type(data[1]))

    def test_calc_temp(self):
        data = Functions.calc_temp(97200, 6598)
        self.assertEqual(float, type(data))
        #self.assertAlmostEqual(1, data, 1)

    def test_calc_electricity_consumption(self):
        data = Functions.calc_electricity_consumption(0)
        self.assertEqual(int, type(data))

    def test_calc_electricity_consumption(self):
        data = Functions.calc_production(0)
        self.assertEqual(int, type(data))
        self.assertEqual(0, data)

    def test_check_JWT(self):
        token = Functions.create_JWT(68)
        data = Functions.check_JWT(token, 68, "Test")
        self.assertEqual(True, data)
        data2 = Functions.check_JWT(token, 1, "Test")
        self.assertEqual(False, data2)


if __name__ == '__main__':
    unittest.main()
