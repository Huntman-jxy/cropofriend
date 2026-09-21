from pathlib import Path
import cv2

from backend.config import DISEASE_MODEL, PEST_MODEL, USE_MODELS, OUTPUTS_DIR


def run_yolo(model_path: Path, image_path: Path, output_name: str):
    from ultralytics import YOLO

    model = YOLO(str(model_path))

    # Temporary lower confidence for testing
    results = model(
        str(image_path),
        conf=0.20,
        verbose=False
    )

    detections = []

    # Create output directory
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUTS_DIR / output_name

    for result in results:
        names = result.names
        boxes = result.boxes

        if boxes is not None:
            for i in range(len(boxes)):
                cls_id = int(boxes.cls[i].item())
                confidence = float(boxes.conf[i].item())
                xyxy = boxes.xyxy[i].tolist()

                detections.append({
                    "label": names.get(cls_id, str(cls_id)),
                    "confidence": round(confidence, 4),
                    "box": [round(v, 1) for v in xyxy],
                })

        # Generate annotated image
        annotated = result.plot()

        # Save annotated image
        cv2.imwrite(str(output_path), annotated)

    return detections, output_path


def preprocess_image(image_path: Path):
    frame = cv2.imread(str(image_path))
    if frame is None:
        raise ValueError("Uploaded file is not a valid image.")

    # Basic preprocessing/validation. YOLO performs its own resize/normalization.
    height, width = frame.shape[:2]

    if width < 128 or height < 128:
        raise ValueError("Please upload a larger crop image.")

    return {
        "width": width,
        "height": height,
    }


def infer(image_path: Path):
    preprocess = preprocess_image(image_path)

    if not USE_MODELS:
        return {
            "disease_detections": [{
                "label": "Early Blight",
                "confidence": 0.92,
                "box": [40, 40, 420, 360],
            }],
            "pest_detections": [{
                "label": "Aphid",
                "confidence": 0.87,
                "box": [120, 100, 210, 190],
            }],
            "severity": "Moderate",
            "demo": True,
            "preprocess": preprocess,
        }

    if DISEASE_MODEL.exists():
        disease, disease_image = run_yolo(
        DISEASE_MODEL,
        image_path,
        "disease_result.jpg"
    )
    else:
        disease = []
        disease_image = None

    if PEST_MODEL.exists():
        pests, pest_image = run_yolo(
            PEST_MODEL,
            image_path,
            "pest_result.jpg"
    )
    else:
        pests = []
        pest_image = None

    # Simple severity proxy for the prototype.
    max_conf = max(
        [d["confidence"] for d in disease + pests],
        default=0.0,
    )

    severity = "Severe" if max_conf >= 0.85 else "Moderate" if max_conf >= 0.60 else "Mild"

    return {
    "disease_detections": disease,
    "pest_detections": pests,
    "severity": severity,
    "demo": False,
    "preprocess": preprocess,

    "disease_image": (
        f"/outputs/{disease_image.name}"
        if disease_image else None
    ),

    "pest_image": (
        f"/outputs/{pest_image.name}"
        if pest_image else None
    ),
    }
