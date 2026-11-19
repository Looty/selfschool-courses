import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "app_starter"
mod = importlib.import_module(TARGET)

from fastapi.testclient import TestClient

WEB = {"name": "web-1", "cpus": 2, "memory_mb": 2048}
DB = {"name": "db-1", "cpus": 8, "memory_mb": 16384}


class FastAPIDrillTest(unittest.TestCase):
    def setUp(self):
        self.app = mod.create_app()
        self.client = TestClient(self.app)

    def test_create_returns_201_with_the_stored_vm(self):
        response = self.client.post("/vms", json=WEB)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {"id": 1, "name": "web-1", "cpus": 2, "memory_mb": 2048, "status": "requested"},
        )

    def test_ids_count_up_and_are_not_reused(self):
        self.assertEqual(self.client.post("/vms", json=WEB).json()["id"], 1)
        self.assertEqual(self.client.post("/vms", json=DB).json()["id"], 2)
        self.client.delete("/vms/2")
        again = self.client.post("/vms", json=DB)
        self.assertEqual(again.status_code, 201)
        self.assertEqual(again.json()["id"], 3)

    def test_get_one(self):
        self.client.post("/vms", json=WEB)
        response = self.client.get("/vms/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "web-1")

    def test_get_missing_is_404_with_detail(self):
        response = self.client.get("/vms/7")
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())

    def test_path_parameter_must_be_an_integer(self):
        response = self.client.get("/vms/abc")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"][0]["loc"], ["path", "vm_id"])

    def test_list_is_ordered_by_id(self):
        self.assertEqual(self.client.get("/vms").json(), [])
        self.client.post("/vms", json=WEB)
        self.client.post("/vms", json=DB)
        response = self.client.get("/vms")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([vm["id"] for vm in response.json()], [1, 2])
        self.assertEqual([vm["name"] for vm in response.json()], ["web-1", "db-1"])

    def test_invalid_bodies_are_422(self):
        bad_bodies = [
            {"name": "web-1", "cpus": 2},
            {"name": "", "cpus": 2, "memory_mb": 2048},
            {"name": "web-1", "cpus": 0, "memory_mb": 2048},
            {"name": "web-1", "cpus": 65, "memory_mb": 2048},
            {"name": "web-1", "cpus": "two", "memory_mb": 2048},
            {"name": "web-1", "cpus": 2, "memory_mb": 64},
            ["web-1", 2, 2048],
        ]
        for body in bad_bodies:
            with self.subTest(body=body):
                response = self.client.post("/vms", json=body)
                self.assertEqual(response.status_code, 422)
                self.assertIsInstance(response.json()["detail"], list)
        self.assertEqual(self.client.get("/vms").json(), [])

    def test_missing_field_is_named_in_the_error(self):
        response = self.client.post("/vms", json={"name": "web-1", "cpus": 2})
        error = response.json()["detail"][0]
        self.assertEqual(error["type"], "missing")
        self.assertEqual(error["loc"], ["body", "memory_mb"])

    def test_duplicate_name_is_409(self):
        self.assertEqual(self.client.post("/vms", json=WEB).status_code, 201)
        response = self.client.post("/vms", json=dict(WEB, cpus=4))
        self.assertEqual(response.status_code, 409)
        self.assertIn("detail", response.json())
        self.assertEqual(len(self.client.get("/vms").json()), 1)

    def test_delete_returns_204_and_removes_the_vm(self):
        self.client.post("/vms", json=WEB)
        response = self.client.delete("/vms/1")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertEqual(self.client.get("/vms/1").status_code, 404)

    def test_delete_is_idempotent(self):
        self.client.post("/vms", json=WEB)
        self.assertEqual(self.client.delete("/vms/1").status_code, 204)
        self.assertEqual(self.client.delete("/vms/1").status_code, 204)
        self.assertEqual(self.client.delete("/vms/99").status_code, 204)

    def test_each_app_has_its_own_store(self):
        self.client.post("/vms", json=WEB)
        other = TestClient(mod.create_app())
        self.assertEqual(other.get("/vms").json(), [])
        self.assertEqual(other.post("/vms", json=WEB).json()["id"], 1)


if __name__ == "__main__":
    unittest.main()
