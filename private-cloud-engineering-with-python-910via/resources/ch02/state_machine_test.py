import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "state_machine_starter"
mod = importlib.import_module(TARGET)
S = mod.VMState


class StateMachineTest(unittest.TestCase):
    def test_starts_pending(self):
        vm = mod.VM("web-1")
        self.assertIs(vm.state, S.PENDING)
        self.assertEqual(vm.history, [S.PENDING])

    def test_happy_path_with_members(self):
        vm = mod.VM("web-1")
        for target in (S.PROVISIONING, S.RUNNING, S.STOPPED, S.DELETED):
            vm.transition(target)
        self.assertIs(vm.state, S.DELETED)
        self.assertEqual(vm.history, [S.PENDING, S.PROVISIONING, S.RUNNING, S.STOPPED, S.DELETED])

    def test_accepts_string_values(self):
        vm = mod.VM("web-1")
        vm.transition("provisioning")
        vm.transition("running")
        self.assertIs(vm.state, S.RUNNING)

    def test_illegal_move_raises_and_changes_nothing(self):
        vm = mod.VM("web-1")
        vm.transition("provisioning")
        with self.assertRaises(mod.IllegalTransition):
            vm.transition(S.STOPPED)
        self.assertIs(vm.state, S.PROVISIONING)
        self.assertEqual(vm.history, [S.PENDING, S.PROVISIONING])

    def test_exception_attributes_and_message(self):
        vm = mod.VM("web-1")
        vm.transition("provisioning")
        vm.transition("running")
        with self.assertRaises(mod.IllegalTransition) as ctx:
            vm.transition("pending")
        self.assertIs(ctx.exception.current, S.RUNNING)
        self.assertIs(ctx.exception.target, S.PENDING)
        self.assertEqual(str(ctx.exception), "illegal transition: running -> pending")

    def test_illegal_transition_is_an_exception(self):
        self.assertTrue(issubclass(mod.IllegalTransition, Exception))

    def test_unknown_string_raises_value_error(self):
        vm = mod.VM("web-1")
        with self.assertRaises(ValueError):
            vm.transition("rebooting")

    def test_deleted_is_final(self):
        vm = mod.VM("web-1")
        vm.transition("deleted")
        for target in S:
            self.assertFalse(vm.can_transition(target))

    def test_error_path(self):
        vm = mod.VM("web-1")
        vm.transition("provisioning")
        vm.transition("error")
        self.assertFalse(vm.can_transition("running"))
        vm.transition("deleted")
        self.assertIs(vm.state, S.DELETED)

    def test_can_transition_does_not_move(self):
        vm = mod.VM("web-1")
        self.assertTrue(vm.can_transition("provisioning"))
        self.assertFalse(vm.can_transition(S.RUNNING))
        self.assertIs(vm.state, S.PENDING)

    def test_stop_and_start_again(self):
        vm = mod.VM("web-1")
        for target in ("provisioning", "running", "stopped", "running", "stopped"):
            vm.transition(target)
        self.assertEqual(len(vm.history), 6)

    def test_vms_do_not_share_history(self):
        a, b = mod.VM("a"), mod.VM("b")
        a.transition("provisioning")
        self.assertEqual(b.history, [S.PENDING])


if __name__ == "__main__":
    unittest.main()
