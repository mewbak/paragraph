#!/usr/bin/env python3

# coding=utf-8
#
# Copyright (c) 2016-2019 Illumina, Inc.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied
# See the License for the specific language governing permissions and limitations
#
import os
import sys
import json
import unittest
import difflib
import tempfile

GRMPY_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", ".."))

sys.path.append(os.path.join(GRMPY_ROOT,
                             "src", "python", "bin"))

GRMPY_INSTALL = None
if "GRMPY_INSTALL" in os.environ:
    GRMPY_INSTALL = os.environ["GRMPY_INSTALL"]


class ADict(dict):
    def __init__(self, *args, **kwargs):
        super(ADict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class TestMultiParagraph(unittest.TestCase):
    def setUp(self):
        self.test_data_dir = os.path.join(
            GRMPY_ROOT, "share", "test-data", "multiparagraph")

    @unittest.skipIf(not GRMPY_INSTALL, "No compiled/install path specified, please set the GRMPY_INSTALL variable to point to an installation.")
    def test_multiparagraph(self):
        bam = os.path.join(self.test_data_dir, "reads.bam")
        ref = os.path.join(self.test_data_dir, "dummy.fa")
        candidates = os.path.join(self.test_data_dir, "candidates.json")
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        output_file.close()

        args = ADict({
            "bam": bam,
            "ref": ref,
            "input": [candidates],
            "output": output_file.name,
            "verbose": False,
            "quiet": True,
            "logfile": None,
            "max_events": None,
            "min_length": 0,
            "extended_output": False,
            "paragraph_threads": 1,
            "threads": 1,
            "scratch_dir": None,
            "keep_scratch": False,
            "paragraph": os.path.join(os.path.dirname(__file__), "module-wrapper.sh") + " " + os.path.join(GRMPY_INSTALL, "bin", "paragraph")
        })
        import multiparagraph
        multiparagraph.run(args)

        expected_fn = os.path.join(self.test_data_dir, "expected.json")
        with open(expected_fn, "rt") as f:
            expected = json.load(f)

        with open(output_file.name, "rt") as f:
            observed = json.load(f)

        for x in expected:
            if "reference" in x["graph"]:
                del x["graph"]["reference"]
            if "commandline" in x["graph"]:
                del x["commandline"]
        for x in observed:
            del x["graph"]["bam"]
            del x["graph"]["reference"]
            del x["commandline"]
            del x["graph"]["alignment_statistics"]  # temporarily remove the check for validation statistics

        expected = json.dumps(expected,
                              sort_keys=True, indent=4, separators=(',', ': ')).splitlines()
        observed = json.dumps(observed,
                              sort_keys=True, indent=4, separators=(',', ': ')).splitlines()

        if expected != observed:
            d = difflib.Differ()
            diff = d.compare(expected, observed)
            print("\n".join(diff))
            print("Difference between observed ({}) and expected ({})".format(
                output_file.name, expected_fn), file=sys.stderr)
        self.assertEqual(expected, observed)
        os.remove(output_file.name)


if __name__ == "__main__":
    unittest.main()
