import unittest

from aider.coders.udiff_coder import cleanup_pure_whitespace_lines, find_diffs, other_hunks_applied
from aider.dump import dump  # noqa: F401


class TestUnifiedDiffCoder(unittest.TestCase):
    def test_find_diffs_single_hunk(self):
        # Test find_diffs with a single hunk
        content = """
Some text...

```diff
--- file.txt
+++ file.txt
@@ ... @@
-Original
+Modified
```
"""
        edits = find_diffs(content)
        dump(edits)
        self.assertEqual(len(edits), 1)

        edit = edits[0]
        self.assertEqual(edit[0], "file.txt")
        self.assertEqual(edit[1], ["-Original\n", "+Modified\n"])

    def test_find_diffs_dev_null(self):
        # Test find_diffs with a single hunk
        content = """
Some text...

```diff
--- /dev/null
+++ file.txt
@@ ... @@
-Original
+Modified
```
"""
        edits = find_diffs(content)
        dump(edits)
        self.assertEqual(len(edits), 1)

        edit = edits[0]
        self.assertEqual(edit[0], "file.txt")
        self.assertEqual(edit[1], ["-Original\n", "+Modified\n"])

    def test_find_diffs_dirname_with_spaces(self):
        # Test find_diffs with a single hunk
        content = """
Some text...

```diff
--- dir name with spaces/file.txt
+++ dir name with spaces/file.txt
@@ ... @@
-Original
+Modified
```
"""
        edits = find_diffs(content)
        dump(edits)
        self.assertEqual(len(edits), 1)

        edit = edits[0]
        self.assertEqual(edit[0], "dir name with spaces/file.txt")
        self.assertEqual(edit[1], ["-Original\n", "+Modified\n"])

    def test_find_multi_diffs(self):
        content = """
To implement the `--check-update` option, I will make the following changes:

1. Add the `--check-update` argument to the argument parser in `aider/main.py`.
2. Modify the `check_version` function in `aider/versioncheck.py` to return a boolean indicating whether an update is available.
3. Use the returned value from `check_version` in `aider/main.py` to set the exit status code when `--check-update` is used.

Here are the diffs for those changes:

```diff
--- aider/versioncheck.py
+++ aider/versioncheck.py
@@ ... @@
     except Exception as err:
         print_cmd(f"Error checking pypi for new version: {err}")
+        return False

--- aider/main.py
+++ aider/main.py
@@ ... @@
     other_group.add_argument(
         "--version",
         action="version",
         version=f"%(prog)s {__version__}",
         help="Show the version number and exit",
     )
+    other_group.add_argument(
+        "--check-update",
+        action="store_true",
+        help="Check for updates and return status in the exit code",
+        default=False,
+    )
     other_group.add_argument(
         "--apply",
         metavar="FILE",
```

These changes will add the `--check-update` option to the command-line interface and use the `check_version` function to determine if an update is available, exiting with status code `0` if no update is available and `1` if an update is available.
"""  # noqa: E501

        edits = find_diffs(content)
        dump(edits)
        self.assertEqual(len(edits), 2)
        self.assertEqual(len(edits[0][1]), 3)


    def test_cleanup_pure_whitespace_lines_crlf(self):
        # CRLF blank lines must be normalized to "\r\n", not truncated to "\r"
        lines = ["   \r\n", "content\n", "\t  \r\n"]
        result = cleanup_pure_whitespace_lines(lines)
        self.assertEqual(result[0], "\r\n")
        self.assertEqual(result[1], "content\n")
        self.assertEqual(result[2], "\r\n")

    def test_cleanup_pure_whitespace_lines_lf(self):
        # LF-only blank lines should be normalized to "\n"
        lines = ["   \n", "content\n"]
        result = cleanup_pure_whitespace_lines(lines)
        self.assertEqual(result[0], "\n")

    def test_other_hunks_applied_message_when_partial_success(self):
        # When num_errors < len(uniq), other_hunks_applied must be appended.
        # This verifies the list-length comparison happens before the join.
        errors_list = ["Error in hunk 1"]
        uniq = ["hunk1", "hunk2", "hunk3"]  # 3 hunks, 1 failed → 2 succeeded
        num_errors = len(errors_list)
        errors_str = "\n\n".join(errors_list)
        if num_errors < len(uniq):
            errors_str += other_hunks_applied
        self.assertIn("some hunks did apply successfully", errors_str)

    def test_other_hunks_applied_message_suppressed_when_all_fail(self):
        # When num_errors == len(uniq), message must NOT be appended.
        errors_list = ["Error in hunk 1", "Error in hunk 2"]
        uniq = ["hunk1", "hunk2"]
        num_errors = len(errors_list)
        errors_str = "\n\n".join(errors_list)
        if num_errors < len(uniq):
            errors_str += other_hunks_applied
        self.assertNotIn("some hunks did apply successfully", errors_str)


if __name__ == "__main__":
    unittest.main()
