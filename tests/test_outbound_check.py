import os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL_DIR = os.path.join(HERE, "..", "tools", "outbound-check")
sys.path.insert(0, TOOL_DIR)
import check

CHECK_PY = os.path.join(TOOL_DIR, "check.py")


def kinds(findings):
    return [k for _, k, _ in findings]


class OutboundCheckTests(unittest.TestCase):
    def test_luhn_card_is_flagged(self):
        found = check.scan("Pay with 4111 1111 1111 1111 today", [])
        self.assertIn("card", kinds(found))

    def test_non_luhn_16_digits_is_not_a_card(self):
        found = check.scan("Order 1234 5678 9012 3456 shipped", [])
        self.assertNotIn("card", kinds(found))

    def test_private_name_flagged_case_insensitive(self):
        found = check.scan("ok\nthanks to JANE example for this", [("name", "Jane Example")])
        self.assertEqual([(2, "name")], [(n, k) for n, k, _ in found])

    def test_example_key_value_is_not_flagged(self):
        text = "api_key = your-key-here\nAPI_KEY=xxxxxxxxxxxx\n"
        self.assertNotIn("secret", kinds(check.scan(text, [])))

    def test_real_looking_key_value_is_flagged(self):
        self.assertIn("secret", kinds(check.scan("password: hunter2hunter2", [])))

    def test_ssn_flagged(self):
        found = check.scan("ssn 123-45-6789", [])
        self.assertIn("ssn", kinds(found))

    def test_owner_domain_email_not_flagged(self):
        terms = [("term", "example.com")]
        self.assertNotIn("email", kinds(check.scan("me@example.com", terms)))
        self.assertIn("email", kinds(check.scan("them@other.org", terms)))
        self.assertIn("email", kinds(check.scan("me@example.com", [])))

    def test_masking_keeps_ends_only(self):
        found = check.scan("key AKIAEXAMPLEEXAMPLE12 here", [])
        self.assertEqual([(1, "secret", "AK...12")], found)

    def test_load_terms(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "t.txt")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("# c\n\nname: Jane Example\naddress: 12 Example Street\nterm: example.com\n")
            self.assertEqual(
                [("name", "Jane Example"), ("address", "12 Example Street"), ("term", "example.com")],
                check.load_terms(p))

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            bad = os.path.join(d, "bad.txt")
            good = os.path.join(d, "good.txt")
            with open(bad, "w", encoding="utf-8") as fh:
                fh.write("hello\nssn 123-45-6789\n")
            with open(good, "w", encoding="utf-8") as fh:
                fh.write("hello there\n")
            r = subprocess.run([sys.executable, CHECK_PY, bad], capture_output=True, text=True)
            self.assertEqual(1, r.returncode)
            self.assertIn("line 2: ssn: 12...89", r.stdout)
            r = subprocess.run([sys.executable, CHECK_PY, good], capture_output=True, text=True)
            self.assertEqual(0, r.returncode)


if __name__ == "__main__":
    unittest.main()
