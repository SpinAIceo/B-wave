from __future__ import annotations

from pathlib import Path


def export_to_onnx(
    model_path: str | Path,
    output_path: str | Path,
    image_size: int = 640,
    opset: int = 17,
    simplify: bool = True,
) -> Path:
    """Convert a YOLOv8 .pt model to optimized ONNX format."""
    from ultralytics import YOLO

    model_path = Path(model_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    model = YOLO(str(model_path))
    export_path = model.export(
        format="onnx",
        imgsz=image_size,
        opset=opset,
        simplify=simplify,
        dynamic=False,
    )

    exported = Path(export_path)
    if exported != output_path:
        exported.rename(output_path)

    _validate_onnx(output_path, image_size)
    return output_path


def _validate_onnx(onnx_path: Path, image_size: int) -> None:
    """Validate ONNX model input/output shapes."""
    import onnx

    model = onnx.load(str(onnx_path))
    onnx.checker.check_model(model)

    inputs = model.graph.input
    assert len(inputs) >= 1, "ONNX model must have at least one input"

    input_shape = [d.dim_value for d in inputs[0].type.tensor_type.shape.dim]
    assert input_shape[2] == image_size and input_shape[3] == image_size, (
        f"Expected input shape [*, *, {image_size}, {image_size}], got {input_shape}"
    )
