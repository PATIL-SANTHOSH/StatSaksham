import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

class TestBackendEndpoints(unittest.TestCase):
    def test_01_health_and_root(self):
        res = client.get("/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["platform"], "STATSAKSHAM")
        self.assertEqual(data["problem_statement"], "SIH26101")

    def test_02_login_learner(self):
        res = client.post("/api/auth/login", json={"employee_id": "OSS1001", "password": "demo123"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["employee_id"], "OSS1001")
        self.assertEqual(data["role"], "LEARNER")
        self.assertIn("access_token", data)

    def test_03_login_admin(self):
        res = client.post("/api/auth/login", json={"employee_id": "ADMIN001", "password": "admin123"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["employee_id"], "ADMIN001")
        self.assertEqual(data["role"], "ADMIN")

    def test_04_get_employee_profile(self):
        # Login first to get token
        login_res = client.post("/api/auth/login", json={"employee_id": "OSS1001", "password": "demo123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = client.get("/api/employees/OSS1001", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["name"], "Ravi Kumar")
        self.assertEqual(data["department"], "National Accounts Division")
        self.assertEqual(data["job_role"], "Statistical Data Analyst")

    def test_05_skill_gaps(self):
        login_res = client.post("/api/auth/login", json={"employee_id": "OSS1001", "password": "demo123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = client.get("/api/employees/OSS1001/skill-gaps", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total_competencies"], 0)
        self.assertGreater(len(data["gaps"]), 0)
        # Check that high priority gaps exist and have reason
        for gap in data["gaps"]:
            if gap["gap"] > 0:
                self.assertTrue(len(gap["reason"]) > 10)
                self.assertIn(gap["priority"], ["High", "Medium", "Low", "None"])

    def test_06_recommendations(self):
        login_res = client.post("/api/auth/login", json={"employee_id": "OSS1001", "password": "demo123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = client.get("/api/employees/OSS1001/recommendations", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total_recommendations"], 0)
        self.assertGreater(len(data["igot_recommendations"]), 0)
        self.assertGreater(len(data["nssta_recommendations"]), 0)

    def test_07_ai_status_and_chat(self):
        res = client.get("/api/ai/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("llm_engine", data)

        # Test chat
        chat_res = client.post("/api/ai/chat", json={
            "employee_id": "OSS1001",
            "message": "Explain what National Accounts GVA is and how to bridge my gap in Python."
        })
        self.assertEqual(chat_res.status_code, 200)
        chat_data = chat_res.json()
        self.assertTrue(len(chat_data["message"]) > 20)
        self.assertEqual(chat_data["role"], "assistant")

    def test_08_admin_analytics(self):
        login_res = client.post("/api/auth/login", json={"employee_id": "ADMIN001", "password": "admin123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = client.get("/api/admin/analytics", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total_employees"], 100)
        self.assertGreater(len(data["top_skill_gaps"]), 0)
        self.assertGreater(len(data["department_summaries"]), 0)

if __name__ == "__main__":
    unittest.main()
