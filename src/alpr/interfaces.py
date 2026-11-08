"""Design-time interfaces only. Protocols do not execute inference or validate artifacts."""
from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

@dataclass(frozen=True)
class RuntimeImage:
    # pixels: uint8 RGB ndarray[H,W,3]; validated by future adapter.
    # sample_id: opaque identifier; never parsed for labels, file paths or bbox.
    sample_id: str
    pixels: Any

@dataclass(frozen=True)
class RuntimeCrop:
    crop_id: str
    sample_id: str
    pixels: Any  # uint8 RGB crop; training labels are passed separately to trainer.

class Detector(Protocol):
    def detect(self, image: RuntimeImage) -> Sequence[Mapping[str, Any]]:
        """DetectionPrediction records in original-image pixel coordinates."""
        ...

class Recognizer(Protocol):
    def recognize(self, crops: Sequence[RuntimeCrop]) -> Sequence[Mapping[str, Any]]:
        """One OCRPrediction per crop, preserving input order; greedy CTC baseline."""
        ...

class Pipeline(Protocol):
    def predict(self, image: RuntimeImage) -> Mapping[str, Any]:
        """Exactly one PipelineResult, including failure states."""
        ...

class Evaluator(Protocol):
    def evaluate(self, predictions: Sequence[Mapping[str, Any]],
                 ground_truth: Sequence[Mapping[str, Any]], *,
                 split_manifest: Mapping[str, Any], mode: str) -> Mapping[str, Any]:
        """GT is evaluator-only; validate full ID coverage and denominator before metrics."""
        ...
