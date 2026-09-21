Put your trained YOLO weights here:

disease_model.pt
pest_model.pt

The code expects standard Ultralytics YOLO .pt models.

Then set USE_MODELS=true.

Do NOT commit large model files to a normal Git repository if your hosting provider has repository-size limits. For production, store model weights in object storage or a model registry and download them during deployment/startup.
