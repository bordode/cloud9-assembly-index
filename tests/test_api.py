import unittest

import main


class Cloud9ApiTests(unittest.TestCase):
    def setUp(self):
        main.app.config["TESTING"] = True
        self.client = main.app.test_client()

    def assert_json_200(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200, path)
        self.assertTrue(response.is_json, path)
        return response.get_json()

    def test_health_route(self):
        payload = self.assert_json_200("/")
        self.assertEqual(payload["status"], "ok")
        self.assertIn("version", payload)
        self.assertIn("threshold_sigma", payload)

    def test_data_route_schema(self):
        payload = self.assert_json_200("/data")
        self.assertIn("version", payload)
        self.assertIsInstance(payload["assembly_index_results"], list)
        self.assertGreater(len(payload["assembly_index_results"]), 0)
        for item in payload["assembly_index_results"]:
            self.assertIn("system", item)
            self.assertIn("A_c", item)

    def test_analyze_route(self):
        payload = self.assert_json_200("/analyze")
        self.assertIn("threshold_sigma", payload)
        self.assertIn("peak_A_c", payload)
        self.assertIn("systems", payload)
        self.assertIn("not a validated physical threshold", payload["threshold_status"])

    def test_empirical_route(self):
        payload = self.assert_json_200("/empirical")
        self.assertIn("sdss_shell", payload)
        self.assertIn("ibm_quantum", payload)

    def test_status_route(self):
        payload = self.assert_json_200("/status")
        self.assertIn("cloud9_version", payload)
        self.assertIn("peak_A_c", payload)
        self.assertIn("server_status", payload)


if __name__ == "__main__":
    unittest.main()
