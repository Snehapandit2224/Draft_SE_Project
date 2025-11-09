import unittest
from app.models import Employee

class TestEmployeeModel(unittest.TestCase):
    def test_employee_creation(self):
        e = Employee(first_name='John', last_name='Doe', email='john.doe@example.com')
        self.assertEqual(e.first_name, 'John')
