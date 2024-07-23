from django.test import TestCase
import subprocess


class BlackFormattingTest(TestCase):

    def test_black_formatting(self):
        result = subprocess.run(
            ["black", "--check", "--diff", "."], capture_output=True, text=True
        )
        if result.returncode != 0:
            self.fail(f"Black formatting issues:\n{result.stdout}\n{result.stderr}")
