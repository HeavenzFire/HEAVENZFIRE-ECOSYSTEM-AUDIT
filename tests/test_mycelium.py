import unittest

from src.heavenzfire_mycelium import LatticeConfig, PixelMycelium


class PixelMyceliumTests(unittest.TestCase):
    def test_three_dimensional_shape_and_cell_count(self):
        grid = PixelMycelium(LatticeConfig((3, 4, 5)))
        self.assertEqual(grid.dimensions, 3)
        self.assertEqual(grid.cell_count, 60)
        self.assertEqual(grid.summary()["active_cells"], 0)

    def test_orthogonal_neighbor_topology_respects_boundaries(self):
        grid = PixelMycelium(LatticeConfig((3, 3)))
        self.assertEqual(len(grid.neighbors((1, 1))), 4)
        self.assertEqual(len(grid.neighbors((0, 0))), 2)
        self.assertNotIn((0, 0), grid.neighbors((0, 0)))

    def test_activation_propagates_deterministically(self):
        config = LatticeConfig((5, 5), diffusion=0.5)
        first = PixelMycelium(config)
        second = PixelMycelium(config)
        first.activate((2, 2))
        second.activate((2, 2))
        first.step(3)
        second.step(3)
        self.assertEqual(first.slice_2d(), second.slice_2d())
        self.assertGreater(first.get((2, 1)), 0.0)
        self.assertGreater(first.summary()["active_cells"], 1)
        self.assertEqual(first.steps, 3)

    def test_periodic_edges_connect_opposite_sides(self):
        grid = PixelMycelium(LatticeConfig((4, 4), wrap_edges=True))
        self.assertIn((3, 0), grid.neighbors((0, 0)))
        self.assertIn((0, 3), grid.neighbors((0, 0)))

    def test_bounds_and_value_validation(self):
        grid = PixelMycelium(LatticeConfig((2, 2)))
        with self.assertRaises(IndexError):
            grid.get((2, 0))
        with self.assertRaises(ValueError):
            grid.set((0, 0), 2.0)
        with self.assertRaises(ValueError):
            PixelMycelium(LatticeConfig((2, 2), diffusion=1.5))

    def test_higher_dimensional_slice(self):
        grid = PixelMycelium(LatticeConfig((2, 3, 4, 5)))
        grid.set((1, 2, 3, 4), 0.75)
        image = grid.slice_2d((1, 2))
        self.assertEqual(len(image), 4)
        self.assertEqual(len(image[0]), 5)
        self.assertEqual(image[3][4], 0.75)


if __name__ == "__main__":
    unittest.main()
