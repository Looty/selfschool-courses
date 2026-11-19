"""Unit tests for app_fastapi.py. No Redis and no worker needed.

Run:  python -m unittest test_api_fastapi -v
"""
import unittest

from fastapi.testclient import TestClient

import tasks
from app_fastapi import create_app
from fakes import FakeQueue, FakeRedis

WEB = {"name": "web-1", "cpus": 2, "memory_mb": 2048}


class FastApiVmTest(unittest.TestCase):
    def setUp(self):
        self.redis = FakeRedis()
        self.queue = FakeQueue()
        self.client = TestClient(create_app(self.redis, self.queue))

    def test_post_returns_202_and_enqueues_one_job(self):
        response = self.client.post("/vms", json=WEB)
        self.assertEqual(response.status_code, 202)
        vm = response.json()
        self.assertEqual(vm["status"], "requested")
        self.assertEqual(vm["cpus"], 2)
        self.assertNotIn("fail", vm)
        self.assertEqual(response.headers["location"], f"/vms/{vm['id']}")
        self.assertEqual([job[1] for job in self.queue.jobs], [(vm["id"],)])

    def test_invalid_body_is_422_with_the_field_named(self):
        response = self.client.post("/vms", json={"name": "web-1", "cpus": 0, "memory_mb": 2048})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"][0]["loc"], ["body", "cpus"])
        extra = self.client.post("/vms", json=dict(WEB, colour="red"))
        self.assertEqual(extra.status_code, 422)
        self.assertEqual(self.queue.jobs, [])

    def test_job_then_get_shows_active(self):
        vm_id = self.client.post("/vms", json=WEB).json()["id"]
        tasks.run_provision(self.redis, vm_id, build_seconds=0)
        response = self.client.get(f"/vms/{vm_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "active")

    def test_missing_vm_is_404(self):
        response = self.client.get("/vms/nope")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "vm nope not found"})

    def test_delete_twice_is_204_both_times(self):
        vm_id = self.client.post("/vms", json=WEB).json()["id"]
        first = self.client.delete(f"/vms/{vm_id}")
        second = self.client.delete(f"/vms/{vm_id}")
        self.assertEqual((first.status_code, second.status_code), (204, 204))
        self.assertEqual(second.content, b"")
        self.assertEqual(self.client.get(f"/vms/{vm_id}").status_code, 404)

    def test_idempotency_key_returns_the_first_vm(self):
        headers = {"Idempotency-Key": "abc-123"}
        first = self.client.post("/vms", json=WEB, headers=headers).json()
        second = self.client.post("/vms", json=WEB, headers=headers).json()
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(len(self.queue.jobs), 1)

    def test_openapi_schema_lists_the_routes(self):
        paths = self.client.get("/openapi.json").json()["paths"]
        self.assertEqual(set(paths), {"/vms", "/vms/{vm_id}", "/healthz"})


if __name__ == "__main__":
    unittest.main()
