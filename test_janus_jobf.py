"""Regression tests for Janus Hydra -> JOBF coupling."""
import unittest
import numpy as np

from janus_hydra import V8State, formation_heads, inverse_heads, inverse_involution_holds
from jobf_v0_2 import JanusOctadialBreathingField, sphere_directions, KEYS


class JanusHydraJobfTests(unittest.TestCase):
    def setUp(self):
        self.model = JanusOctadialBreathingField(dt=.01)

    def test_five_forward_and_inverse_heads(self):
        state = V8State(.8, .7, .75, .25, .65, .6, .72, .55)
        self.assertEqual(len(formation_heads(state)), 5)
        self.assertEqual(len(inverse_heads(state)), 5)
        self.assertTrue(inverse_involution_holds())

    def test_eight_channels_are_driven(self):
        result = self.model.channel_state(.37)
        self.assertEqual(len(result[1]), 8)
        self.assertEqual(len(result[5]), 8)
        self.assertEqual(len(result[6]), 8)
        self.assertEqual(len(KEYS), 8)

    def test_uhfe_udfe_are_distinct(self):
        _, _, _, _, _, uh, ud, _ = self.model.channel_state(.41)
        self.assertFalse(np.allclose(uh, ud))

    def test_boundary_is_positive_and_finite(self):
        directions = sphere_directions(256)
        rho, _, _, _ = self.model.boundary(directions, .8)
        self.assertTrue(np.all(np.isfinite(rho)))
        self.assertTrue(np.all(rho > 0))

    def test_cross_polytope_domain_not_split(self):
        directions = np.vstack([np.eye(8), -np.eye(8)])
        rho, rho0, _, _ = self.model.boundary(directions, .2)
        self.assertEqual(rho.shape, (16,))
        self.assertTrue(np.all(rho0 > 0))
        # Both signs of every axis are present in the same evaluated domain.
        self.assertEqual(directions.shape[0], 16)


if __name__ == "__main__":
    unittest.main()
