import unittest

import numpy as np

from cloud9_ssbm import (
    ObservationConfig,
    SignalSimulator,
    StellarParameters,
    StellarBroadeningKernel,
    WidthAwareSETIPipeline,
    run_production_test,
)


class SSBMSmokeTests(unittest.TestCase):
    def test_narrowband_signal_is_finite(self):
        frequencies = np.linspace(1.0e9, 1.001e9, 1001)
        spectrum = SignalSimulator(42).generate_narrowband(
            frequencies, center_freq=1.0005e9, width_hz=100.0
        )
        self.assertEqual(spectrum.shape, frequencies.shape)
        self.assertTrue(np.all(np.isfinite(spectrum)))
        self.assertGreater(float(spectrum.max()), 0.0)

    def test_broadening_preserves_shape(self):
        config = ObservationConfig()
        frequencies = config.frequencies
        spectrum = np.ones_like(frequencies)
        result = StellarBroadeningKernel(StellarParameters()).apply_broadening(
            spectrum, frequencies
        )
        self.assertEqual(result.shape, spectrum.shape)
        self.assertTrue(np.all(np.isfinite(result)))

    def test_detection_result_is_explicitly_synthetic(self):
        config = ObservationConfig()
        spectrum, metadata = SignalSimulator(42).generate_broadened_scenario(
            config, StellarParameters()
        )
        result = WidthAwareSETIPipeline().detect(
            spectrum, config.frequencies, StellarParameters(), metadata
        )
        self.assertIn("detected", result)
        self.assertIsInstance(result["detected"], bool)
        self.assertEqual(result["data_kind"], "synthetic")
        self.assertIn("not evidence of an extraterrestrial signal", result["interpretation"])

    def test_smoke_entrypoint(self):
        result = run_production_test()
        self.assertEqual(result["smoke_test"], "completed")
        self.assertEqual(result["data_kind"], "synthetic")


if __name__ == "__main__":
    unittest.main()
