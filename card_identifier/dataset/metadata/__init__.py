from multiprocessing import Lock

import jsonlines


class JSONLinesWriter:
    def __init__(self, filename):
        self.filename = filename
        self.lock = Lock()

    def write(self, data):
        with self.lock:  # Ensure thread-safe writing
            with jsonlines.open(self.filename, mode='a') as writer:
                writer.write(data)


metadata_writer = JSONLinesWriter('metadata.jsonl')
