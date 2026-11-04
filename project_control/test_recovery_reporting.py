import unittest

from validate_control_plane import validate_recovery_reporting


class RecoveryReportingTests(unittest.TestCase):
    def setUp(self):
        self.state = {"active_recovery": {
            "package": "Recovery Package 009",
            "branch": "implementation/repair",
            "accepted": False,
        }}
        self.ledger = (
            "ACTIVE_PACKAGE: `Recovery Package 009`\n"
            "ACTIVE_BRANCH: `implementation/repair`\n"
            "NEXT_READY_REC: `NONE`\n"
        )

    def test_current_unaccepted_package_is_reported_truthfully(self):
        self.assertEqual(validate_recovery_reporting(self.state, self.ledger), [])

    def test_handoff_cannot_hide_active_repair_as_none(self):
        ledger = self.ledger.replace("ACTIVE_PACKAGE: `Recovery Package 009`", "ACTIVE_PACKAGE: `NONE`")
        self.assertTrue(validate_recovery_reporting(self.state, ledger))

    def test_handoff_cannot_release_next_rec_before_current_repair(self):
        ledger = self.ledger.replace("NEXT_READY_REC: `NONE`", "NEXT_READY_REC: `REC-20`")
        self.assertTrue(validate_recovery_reporting(self.state, ledger))

    def test_unrecorded_package_cannot_become_a_second_runtime_authority(self):
        self.assertTrue(validate_recovery_reporting({}, self.ledger))


if __name__ == "__main__":
    unittest.main()
