# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import subprocess
import unittest
from unittest.mock import patch

from system.arch import current_arch


class TestArch(unittest.TestCase):
    def test_current_arch(self):
        self.assertTrue(current_arch() in ["x64", "arm64"])

    @patch("subprocess.check_output")
    def test_x64_arch(self, mock_subprocess):
        mock_subprocess.return_value = "x86_64".encode()
        self.assertTrue(current_arch() == "x64")

    @patch("subprocess.check_output")
    def test_arm64_arch(self, mock_subprocess):
        mock_subprocess.return_value = "aarch64".encode()
        self.assertTrue(current_arch() == "arm64")
        mock_subprocess.return_value = "arm64".encode()
        self.assertTrue(current_arch() == "arm64")

    @patch("subprocess.check_output")
    def test_invalid_arch(self, mock_subprocess):
        mock_subprocess.return_value = "invalid".encode()
        with self.assertRaises(ValueError) as context:
            current_arch()
        subprocess.check_output.assert_called_with(["uname", "-m"])
        self.assertEqual(
            "Unsupported architecture: invalid", context.exception.__str__()
        )
