import os
import sys

import pytest

if __name__ == "__main__":
    os.environ["APP_SETTINGS"] = "TestingConfig"
    covreport = "term-missing"
    if len(sys.argv) > 1:
        covreport = sys.argv[1]
    exitcode = pytest.main(
        ["--cov-report", covreport, "--cov", "response_operations_ui", "--capture", "no", "--ignore=node_modules"]
    )
    sys.exit(exitcode)
