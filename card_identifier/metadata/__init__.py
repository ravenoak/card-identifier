from dataclasses import dataclass
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


@dataclass
class TransformationMetadata:
    transformation_class: str
    type: str
    method: str
    parameters: dict


@dataclass
class ImageMetadata:
    image_path: str
    image_hash: str
    image_id: str
    transformation_metadata: list[TransformationMetadata]


metadata_writer = JSONLinesWriter('metadata.jsonl')
