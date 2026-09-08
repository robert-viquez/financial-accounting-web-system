from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from config.settings import env_bool, env_list


class EnvironmentParsingTests(SimpleTestCase):
    @patch.dict("os.environ", {"FAWS_TEST_LIST": " one.example, two.example ,,"})
    def test_env_list_trims_values_and_ignores_empty_items(self):
        self.assertEqual(env_list("FAWS_TEST_LIST"), ["one.example", "two.example"])

    @patch.dict("os.environ", {"FAWS_TEST_BOOL": "YeS"})
    def test_env_bool_accepts_common_true_values(self):
        self.assertTrue(env_bool("FAWS_TEST_BOOL"))


class HealthEndpointTests(TestCase):
    def test_health_endpoint_reports_ready_without_authentication(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
