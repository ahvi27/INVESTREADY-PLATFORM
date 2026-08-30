import os
import tempfile
import unittest

from investready.database import add_followup, add_investor, connect, get_followups, get_investors, initialize, toggle_followup, update_stage


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        handle, path = tempfile.mkstemp(suffix=".db")
        os.close(handle)
        self.path = path
        os.environ["INVESTREADY_DB"] = path
        initialize()
        self.data = {"company":"Test Industries","country":"Ethiopia","sector":"Manufacturing","investment_usd_m":50,"jobs":500,"export_percent":50,"environmental_score":5,"financial_score":5,"technology_score":5,"readiness_score":5,"stage":"Prospect","status":"Active"}

    def tearDown(self):
        os.unlink(self.path)

    def test_add_investor_calculates_score(self):
        investor_id = add_investor(self.data)
        investor = get_investors()[0]
        self.assertEqual(investor["id"], investor_id)
        self.assertEqual(investor["total_score"], 50)

    def test_duplicate_company_rejected(self):
        add_investor(self.data)
        with self.assertRaises(Exception):
            add_investor(self.data)

    def test_update_stage(self):
        investor_id = add_investor(self.data)
        update_stage(investor_id, "Engaged")
        self.assertEqual(get_investors()[0]["stage"], "Engaged")

    def test_invalid_stage_rejected(self):
        investor_id = add_investor(self.data)
        with self.assertRaises(ValueError):
            update_stage(investor_id, "Unknown")

    def test_followup_lifecycle(self):
        investor_id = add_investor(self.data)
        followup_id = add_followup(investor_id, "2026-09-01", "Call investor", "Aliya")
        self.assertEqual(len(get_followups()), 1)
        toggle_followup(followup_id, True)
        self.assertEqual(get_followups()[0]["completed"], 1)

    def test_foreign_keys_enabled(self):
        with connect() as db:
            self.assertEqual(db.execute("PRAGMA foreign_keys").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
