import io


def local_inference(image_bytes: bytes):
    try:
        import torch
        from torchvision import transforms, models
        from PIL import Image

        model = models.mobilenet_v2(pretrained=True)
        model.eval()

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        tensor = transform(img).unsqueeze(0)

        with torch.no_grad():
            logits = model(tensor)
            probs = torch.nn.functional.softmax(logits, dim=1)
            topk = probs[0].topk(3)
            indices = topk.indices.tolist()
            values = topk.values.tolist()

        candidates = [
            {"label": f"imagenet_class_{idx}", "confidence": float(conf)}
            for idx, conf in zip(indices, values)
        ]

        return {
            "label": candidates[0]["label"],
            "confidence": candidates[0]["confidence"],
            "tags": [c["label"] for c in candidates],
            "candidates": candidates,
            "note": "Placeholder MobileNetV2 (ImageNet).",
        }

    except Exception as e:
        return {"label": "unknown", "confidence": 0.0, "tags": [], "candidates": [], "error": str(e)}
import io
def local_inference(image_bytes: bytes):
    try:
        import torch
        from torchvision import transforms, models
        from PIL import Image
        model = models.mobilenet_v2(pretrained=True)
        model.eval()
        img = Image.open(io.BytesIO(image_bytes)).convert(\"RGB\")
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
        import io


        def local_inference(image_bytes: bytes):
            try:
                import torch
                from torchvision import transforms, models
                from PIL import Image

                model = models.mobilenet_v2(pretrained=True)
                model.eval()

                img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                transform = transforms.Compose([
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
                ])
                tensor = transform(img).unsqueeze(0)

                with torch.no_grad():
                    logits = model(tensor)
                    probs = torch.nn.functional.softmax(logits, dim=1)
                    topk = probs[0].topk(3)
                    indices = topk.indices.tolist()
                    values = topk.values.tolist()

                candidates = [
                    {"label": f"imagenet_class_{idx}", "confidence": float(conf)}
                    for idx, conf in zip(indices, values)
                ]

                return {
                    "label": candidates[0]["label"],
                    "confidence": candidates[0]["confidence"],
                    "tags": [c["label"] for c in candidates],
                    "candidates": candidates,
                    "note": "Placeholder MobileNetV2 (ImageNet).",
                }

            except Exception as e:
                return {"label": "unknown", "confidence": 0.0, "tags": [], "candidates": [], "error": str(e)}
