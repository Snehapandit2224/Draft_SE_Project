import unittest
from unittest.mock import patch
from app import create_app, db

class HealthCheckTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_health_check_success(self):
        """Test health check endpoint returns 200 on success."""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        json_response = response.get_json()
        self.assertEqual(json_response['application_status'], 'ok')
        self.assertEqual(json_response['dependencies']['database'], 'ok')

    @patch('app.health.api.db.session.execute')
    def test_health_check_db_error(self, mock_execute):
        """Test health check endpoint returns 500 on db error."""
        mock_execute.side_effect = Exception('DB error')
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 500)
        json_response = response.get_json()
        self.assertEqual(json_response['application_status'], 'error')
        self.assertEqual(json_response['dependencies']['database'], 'error')

    @patch('app.health.api.shutil.disk_usage')
    def test_health_check_disk_usage(self, mock_disk_usage):
        """Test health check endpoint returns correct disk usage."""
        mock_disk_usage.return_value = (10 * 1024**3, 5 * 1024**3, 5 * 1024**3)
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        json_response = response.get_json()
        self.assertEqual(json_response['dependencies']['disk_space']['total'], '10 GB')
        self.assertEqual(json_response['dependencies']['disk_space']['used'], '5 GB')
        self.assertEqual(json_response['dependencies']['disk_space']['free'], '5 GB')
        self.assertEqual(json_response['dependencies']['disk_space']['percent_used'], '50.00%')

    @patch('app.health.api.psutil.virtual_memory')
    def test_health_check_memory_usage(self, mock_virtual_memory):
        """Test health check endpoint returns correct memory usage."""
        class MockVirtualMemory:
            def __init__(self, total, available, percent):
                self.total = total
                self.available = available
                self.percent = percent
        
        mock_virtual_memory.return_value = MockVirtualMemory(16 * 1024**3, 8 * 1024**3, 50.0)
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        json_response = response.get_json()
        self.assertEqual(json_response['dependencies']['memory']['total'], '16 GB')
        self.assertEqual(json_response['dependencies']['memory']['available'], '8 GB')
        self.assertEqual(json_response['dependencies']['memory']['percent_used'], '50.0%')

if __name__ == '__main__':
    unittest.main()
