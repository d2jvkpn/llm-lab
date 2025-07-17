#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

import gradio as gr


class LabLogger(gr.FlaggingCallback):
    def __init__(self, keys, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.keys = keys

        self.log_dir.mkdir(exist_ok=True)
        self.filepath = self.log_dir / f"flagging.{datetime.now().strftime('%F')}.jsonl"
        self.file = None

    def setup(self, components, flagging_options):
        #print("~~~ Flagging setup")
        if not self.filepath.exists():
            self.file = open(self.filepath, "w", encoding="utf-8")
        else:
            self.file = open(self.filepath, "a", encoding="utf-8")

    def flag(self, flag_data, flag_option=None, username=None):
        timestamp = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%:z")
        record = {"timestamp": timestamp}

        if flag_option is not None:
            record["flag"] = flag_option.lower()

        for i, k in enumerate(self.keys):
            record[k] = flag_data[i]

        json.dump(record, self.file, ensure_ascii=False)
        self.file.write("\n")
        self.file.flush()

    def close(self):
        #print("~~~ Closing flagging callback and cleaning up")
        if self.file is not None:
            self.file.close()
