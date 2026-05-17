"""
Full evaluation runner.
"""

import pytest
import subprocess


def run_all_tests():

    result = subprocess.run(
        ["pytest", "app/tests", "-v"]
    )

    return result.returncode


if __name__ == "__main__":

    code = run_all_tests()

    if code == 0:

        print(
            "\nAll evaluation tests passed."
        )

    else:

        print(
            "\nSome tests failed."
        )