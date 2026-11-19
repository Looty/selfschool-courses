"""Unit tests for app.py and tasks.py. No Redis and no worker needed.

Run:  python -m unittest test_api -v      (or: python test_api.py)
"""
import unittest

import tasks
from app import create_app
from fakes import FakeQueue, FakeRedis

WEB = {"name": "web-1", "cpus": 2, "memory_mb": 2048}


class VmApiTest(unittest.TestCase):
    def setUp(self):
        self.redis = FakeRedis()
        self.queue = FakeQueue()
        self.client = create_app(self.redis, self.queue).test_client()

    def create(self, body=WEB, **kwargs):
        return self.client.post("/vms", json=body, **kwargs)

    def run_job(self, vm_id):
        return tasks.run_provision(self.redis, vm_id, build_seconds=0)

    def test_post_returns_202_and_enqueues_one_job(self):
        response = self.create()
        self.assertEqual(response.status_code, 202)
        vm = response.json
        self.assertEqual(vm["status"], "requested")
        self.assertEqual(vm["cpus"], 2)
        self.assertEqual(response.headers["Location"], f"/vms/{vm['id']}")
        self.assertEqual(len(self.queue.jobs), 1)
        func, args, options = self.queue.jobs[0]
        self.assertIs(func, tasks.provision)
        self.assertEqual(args, (vm["id"],))
        self.assertEqual(options["job_id"], f"provision-{vm['id']}")
        self.assertIs(options["retry"], tasks.RETRY)

    def test_invalid_bodies_are_400_and_enqueue_nothing(self):
        bad_bodies = [
            None,
            ["web-1"],
            {"name": "web-1", "cpus": 2},
            {"name": "", "cpus": 2, "memory_mb": 2048},
            {"name": "web-1", "cpus": 0, "memory_mb": 2048},
            {"name": "web-1", "cpus": True, "memory_mb": 2048},
            {"name": "web-1", "cpus": 2, "memory_mb": 2048, "fail": "yes"},
            {"name": "web-1", "cpus": 2, "memory_mb": 2048, "colour": "red"},
        ]
        for body in bad_bodies:
            with self.subTest(body=body):
                response = self.create(body)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json["error"], "Bad Request")
        self.assertEqual(self.queue.jobs, [])

    def test_errors_from_routing_are_json(self):
        missing = self.client.get("/vms/nope")
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(missing.json["error"], "Not Found")
        wrong_method = self.client.put("/vms/abc", json=WEB)
        self.assertEqual(wrong_method.status_code, 405)
        self.assertEqual(wrong_method.json["error"], "Method Not Allowed")

    def test_job_moves_vm_to_active(self):
        vm_id = self.create().json["id"]
        self.assertEqual(self.run_job(vm_id), "active")
        vm = self.client.get(f"/vms/{vm_id}").json
        self.assertEqual(vm["status"], "active")
        self.assertEqual(vm["attempts"], 0)

    def test_job_is_idempotent(self):
        vm_id = self.create().json["id"]
        self.run_job(vm_id)
        before = self.redis.hgetall(tasks.vm_key(vm_id))
        self.assertEqual(self.run_job(vm_id), "active")
        self.assertEqual(self.redis.hgetall(tasks.vm_key(vm_id)), before)

    def test_job_resumes_a_vm_left_in_building(self):
        vm_id = self.create().json["id"]
        self.redis.hset(tasks.vm_key(vm_id), {"status": "building"})   # a worker died here
        self.assertEqual(self.run_job(vm_id), "active")

    def test_failing_vm_ends_in_error_after_max_attempts(self):
        vm_id = self.create(dict(WEB, fail=True)).json["id"]
        for attempt in range(1, tasks.MAX_ATTEMPTS + 1):
            with self.assertRaises(RuntimeError):
                self.run_job(vm_id)
            vm = self.client.get(f"/vms/{vm_id}").json
            self.assertEqual(vm["attempts"], attempt)
            expected = "error" if attempt == tasks.MAX_ATTEMPTS else "building"
            self.assertEqual(vm["status"], expected)
        self.assertEqual(vm["error"], "simulated hypervisor error")
        self.assertEqual(self.run_job(vm_id), "error")   # one more run changes nothing

    def test_delete_is_idempotent_and_hides_the_vm(self):
        vm_id = self.create().json["id"]
        self.assertEqual(self.client.delete(f"/vms/{vm_id}").status_code, 204)
        self.assertEqual(self.client.delete(f"/vms/{vm_id}").status_code, 204)
        self.assertEqual(self.client.delete("/vms/never-existed").status_code, 204)
        self.assertEqual(self.client.get(f"/vms/{vm_id}").status_code, 404)
        self.assertEqual(self.redis.ttl(tasks.vm_key(vm_id)), 3600)

    def test_job_does_nothing_for_a_deleted_vm(self):
        vm_id = self.create().json["id"]
        self.client.delete(f"/vms/{vm_id}")
        self.assertEqual(self.run_job(vm_id), "deleted")
        self.assertEqual(self.redis.hget(tasks.vm_key(vm_id), "status"), "deleted")

    def test_job_for_a_vm_that_is_gone_does_not_recreate_it(self):
        self.assertIsNone(self.run_job("gone"))
        self.assertEqual(self.redis.hgetall(tasks.vm_key("gone")), {})

    def test_idempotency_key_returns_the_first_vm(self):
        headers = {"Idempotency-Key": "8e03978e-40d5-43e8-bc93-6894a57f9324"}
        first = self.create(headers=headers)
        second = self.create(headers=headers)
        self.assertEqual(second.status_code, 202)
        self.assertEqual(second.json["id"], first.json["id"])
        self.assertEqual(len(self.queue.jobs), 1)

    def test_idempotency_key_in_flight_is_409(self):
        self.redis.set("idem:k1", "not-yet-stored", nx=True, ex=60)
        response = self.create(headers={"Idempotency-Key": "k1"})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.queue.jobs, [])

    def test_lock_is_exclusive_and_released(self):
        with tasks.vm_lock(self.redis, "x"):
            with self.assertRaises(tasks.LockTimeout):
                with tasks.vm_lock(self.redis, "x", wait_seconds=0.1):
                    pass
        self.assertIsNone(self.redis.get("lock:vm:x"))

    def test_healthz(self):
        self.assertEqual(self.client.get("/healthz").json, {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
