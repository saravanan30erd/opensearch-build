# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import logging
import os
import subprocess
import tempfile
from pathlib import Path


class GitRepository:
    """
    This class checks out a Git repository at a particular ref into an empty named directory (or temporary a directory if no named directory is given).
    Temporary directories will be automatically deleted when the GitRepository object goes out of scope; named directories will be left alone.
    Clients can obtain the actual commit ID by querying the "sha" attribute, and the temp directory name with "dir".
    """

    def __init__(self, url, ref, directory=None, working_subdirectory=None):
        self.url = url
        self.ref = ref
        if directory is None:
            self.temp_dir = tempfile.TemporaryDirectory()
            self.dir = self.temp_dir.name
        else:
            self.temp_dir = None
            self.dir = directory
            os.makedirs(self.dir, exist_ok=False)

        # Check out the repository
        self.working_subdirectory = working_subdirectory
        self.execute_silent("git init", self.dir)
        self.execute_silent(f"git remote add origin {self.url}", self.dir)
        self.execute_silent(f"git fetch --depth 1 origin {self.ref}", self.dir)
        self.execute_silent("git checkout FETCH_HEAD", self.dir)
        self.sha = self.output("git rev-parse HEAD", self.dir)
        logging.info(f"Checked out {self.url}@{self.ref} into {self.dir} at {self.sha}")

    @property
    def working_directory(self):
        if self.working_subdirectory:
            return os.path.join(self.dir, self.working_subdirectory)
        else:
            return self.dir

    def execute_silent(self, command, cwd=None):
        cwd = cwd or self.working_directory
        logging.info(f'Executing "{command}" in {cwd}')
        subprocess.check_call(
            command,
            cwd=cwd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def output(self, command, cwd=None):
        cwd = cwd or self.working_directory
        logging.info(f'Executing "{command}" in {cwd}')
        return subprocess.check_output(command, cwd=cwd, shell=True).decode().strip()

    def execute(self, command, cwd=None):
        cwd = cwd or self.working_directory
        logging.info(f'Executing "{command}" in {cwd}')
        subprocess.check_call(command, cwd=cwd, shell=True)

    def path(self, subdirname=None):
        dirname = self.dir
        if subdirname:
            dirname = os.path.join(self.dir, subdirname)
        return Path(dirname)
