@echo off
REM Copy the best ONNX model into the poc-web backend before Docker build / Railway deploy
set SRC=..\..\runs\detect\runs\train\bwave-yolo26s-v1\weights\best.onnx
set DST=backend\model\best.onnx

if not exist "%SRC%" (
  echo ERROR: Model not found at %SRC%
  echo Make sure best.onnx exists at runs/detect/runs/train/bwave-yolo26s-v1/weights/
  exit /b 1
)

copy "%SRC%" "%DST%"
echo Copied model to %DST%
