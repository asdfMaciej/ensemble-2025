import requests
import torch
import torch.nn as nn
import os
from torchvision import models


TOKEN = ...                         # Your token here
URL = "149.156.182.9:6060/task-3/submit"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


if __name__ == '__main__':
    os.makedirs("out/models", exist_ok=True)

    #### SUBMISSION ####

    # Create a dummy model
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.weight.shape[1], 10)
    torch.save(model.state_dict(), "out/models/dummy_submission.pt")

    #### Tests ####
    # (these are being ran on the eval endpoint for every submission)

    allowed_models = {
        "resnet18": models.resnet18,
        "resnet34": models.resnet34,
        "resnet50": models.resnet50,
    }
    with open("out/models/dummy_submission.pt", "rb") as f:
        try:
            model: torch.nn.Module = allowed_models["resnet18"](weights=None)
            model.fc = torch.nn.Linear(model.fc.weight.shape[1], 10)
        except Exception as e:
            raise Exception(
                f"Invalid model class, {e=}, only {allowed_models.keys()} are allowed",
            )
        try:
            state_dict = torch.load(f, map_location=torch.device("cpu"))
            model.load_state_dict(state_dict, strict=True)
            model.eval()
            out = model(torch.randn(1, 3, 32, 32))
        except Exception as e:
            raise Exception(f"Invalid model, {e=}")

        assert out.shape == (1, 10), "Invalid output shape"


    # Send the model to the server
    response = requests.post(
        URL,
        headers={
            "token": TOKEN,
            "model-name": "resnet18"
        },
        files={
            "model_state_dict": open("out/models/dummy_submission.pt", "rb")
        }
    )

    # Should be 400, the clean accuracy is too low
    print(response.status_code, response.text)