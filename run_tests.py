import os
import sys

import pytest

if __name__ == "__main__":
    os.environ["APP_SETTINGS"] = "TestingConfig"
    exitcode = pytest.main(
        [
            "--cov-report",
            "term-missing",
            "--cov",
            "response_operations_ui",
            "--capture",
            "no",
            "--ignore=node_modules",
        ]
    )
    sys.exit(exitcode)
