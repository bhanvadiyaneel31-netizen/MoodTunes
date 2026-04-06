import argparse, torch
from ml.model import load_model


def export(weights_path, output="ml/weights/emotion_cnn.onnx"):
    model = load_model(weights_path, "cpu")
    dummy = torch.randn(1, 1, 48, 48)
    torch.onnx.export(model, dummy, output, export_params=True, opset_version=17,
                      input_names=["image"], output_names=["logits"],
                      dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}})
    import onnxruntime as ort
    sess = ort.InferenceSession(output)
    out = sess.run(None, {"image": dummy.numpy()})
    print(f"Exported: {output} | shape: {out[0].shape}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--weights", default="ml/weights/emotion_cnn.pth")
    p.add_argument("--output", default="ml/weights/emotion_cnn.onnx")
    args = p.parse_args()
    export(args.weights, args.output)
