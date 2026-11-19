import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "app_starter"
mod = importlib.import_module(TARGET)

WEB = {"name": "web-1", "cpus": 2, "memory_mb": 2048}
DB = {"name": "db-1", "cpus": 8, "memory_mb": 16384}


class FlaskDrillTest(unittest.TestCase):
    def setUp(self):
        self.app = mod.create_app()
        self.app.testing = True
        self.client = self.app.test_client()

    def test_create_returns_201_with_the_stored_vm(self):
        response = self.client.post("/vms", json=WEB)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json,
            {"id": 1, "name": "web-1", "cpus": 2, "memory_mb": 2048, "status": "requested"},
        )
        self.assertEqual(response.headers["Location"], "/vms/1")

    def test_ids_count_up_and_are_not_reused(self):
        self.assertEqual(self.client.post("/vms", json=WEB).json["id"], 1)
        self.assertEqual(self.client.post("/vms", json=DB).json["id"], 2)
        self.client.delete("/vms/2")
        again = self.client.post("/vms", json=DB)
        self.assertEqual(again.status_code, 201)
        self.assertEqual(again.json["id"], 3)

    def test_get_one(self):
        self.client.post("/vms", json=WEB)
        response = self.client.get("/vms/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "web-1")

    def test_get_missing_is_404_json(self):
        response = self.client.get("/vms/7")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.is_json)
        self.assertIn("error", response.json)

    def test_list_is_ordered_by_id(self):
        self.assertEqual(self.client.get("/vms").json, [])
        self.client.post("/vms", json=WEB)
        self.client.post("/vms", json=DB)
        response = self.client.get("/vms")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([vm["id"] for vm in response.json], [1, 2])
        self.assertEqual([vm["name"] for vm in response.json], ["web-1", "db-1"])

    def test_invalid_bodies_are_400(self):
        bad_bodies = [
            {"name": "web-1", "cpus": 2},
            {"name": "", "cpus": 2, "memory_mb": 2048},
            {"name": "web-1", "cpus": 0, "memory_mb": 2048},
            {"name": "web-1", "cpus": "2", "memory_mb": 2048},
            {"name": "web-1", "cpus": True, "memory_mb": 2048},
            {"name": "web-1", "cpus": 2, "memory_mb": 64},
            ["web-1", 2, 2048],
        ]
        for body in bad_bodies:
            with self.subTest(body=body):
                response = self.client.post("/vms", json=body)
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.json)
        self.assertEqual(self.client.get("/vms").json, [])

    def test_body_that_is_not_json_is_400(self):
        response = self.client.post("/vms", data="name=web-1", content_type="text/plain")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_duplicate_name_is_409(self):
        self.assertEqual(self.client.post("/vms", json=WEB).status_code, 201)
        response = self.client.post("/vms", json=dict(WEB, cpus=4))
        self.assertEqual(response.status_code, 409)
        self.assertIn("error", response.json)
        self.assertEqual(len(self.client.get("/vms").json), 1)

    def test_delete_returns_204_and_removes_the_vm(self):
        self.client.post("/vms", json=WEB)
        response = self.client.delete("/vms/1")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, b"")
        self.assertEqual(self.client.get("/vms/1").status_code, 404)

    def test_delete_is_idempotent(self):
        self.client.post("/vms", json=WEB)
        self.assertEqual(self.client.delete("/vms/1").status_code, 204)
        self.assertEqual(self.client.delete("/vms/1").status_code, 204)
        self.assertEqual(self.client.delete("/vms/99").status_code, 204)

    def test_routing_errors_are_json_too(self):
        unknown = self.client.get("/nope")
        self.assertEqual(unknown.status_code, 404)
        self.assertIn("error", unknown.json)
        not_an_int = self.client.get("/vms/abc")
        self.assertEqual(not_an_int.status_code, 404)
        self.assertIn("error", not_an_int.json)
        wrong_method = self.client.put("/vms", json=WEB)
        self.assertEqual(wrong_method.status_code, 405)
        self.assertIn("error", wrong_method.json)

    def test_each_app_has_its_own_store(self):
        self.client.post("/vms", json=WEB)
        other = mod.create_app().test_client()
        self.assertEqual(other.get("/vms").json, [])
        self.assertEqual(other.post("/vms", json=WEB).json["id"], 1)


if __name__ == "__main__":
    unittest.main()
