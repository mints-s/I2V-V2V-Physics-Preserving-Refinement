"""Paired video dataset for minimal DyRefHead overfit experiments."""

from __future__ import annotations

from pathlib import Path

import torch
from torch.utils.data import Dataset


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENES = ("scene01_seed0", "scene02_seed0", "scene03_seed0")


def _read_video_with_cv2(path: Path, max_frames: int | None, resize: tuple[int, int] | None) -> torch.Tensor:
    import cv2
    import numpy as np

    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open video: {path}")

    frames: list[np.ndarray] = []
    try:
        while max_frames is None or len(frames) < max_frames:
            ok, frame_bgr = capture.read()
            if not ok:
                break
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            if resize is not None:
                width, height = resize
                frame_rgb = cv2.resize(frame_rgb, (width, height), interpolation=cv2.INTER_AREA)
            frames.append(frame_rgb)
    finally:
        capture.release()

    if not frames:
        raise RuntimeError(f"No frames decoded from video: {path}")

    array = np.stack(frames, axis=0).astype("float32") / 255.0
    return torch.from_numpy(array).permute(3, 0, 1, 2).contiguous()


def _read_video_with_imageio(path: Path, max_frames: int | None, resize: tuple[int, int] | None) -> torch.Tensor:
    import imageio.v3 as iio
    import numpy as np
    from PIL import Image

    frames = []
    for idx, frame in enumerate(iio.imiter(path)):
        if max_frames is not None and idx >= max_frames:
            break
        if frame.ndim == 2:
            frame = np.repeat(frame[..., None], 3, axis=2)
        frame = frame[..., :3]
        if resize is not None:
            width, height = resize
            frame = np.asarray(Image.fromarray(frame).resize((width, height), Image.Resampling.BILINEAR))
        frames.append(frame)

    if not frames:
        raise RuntimeError(f"No frames decoded from video: {path}")

    array = np.stack(frames, axis=0).astype("float32") / 255.0
    return torch.from_numpy(array).permute(3, 0, 1, 2).contiguous()


def read_video_tensor(
    path: str | Path,
    max_frames: int | None = 32,
    resize: int | tuple[int, int] | None = 128,
) -> torch.Tensor:
    """Read an RGB video as a float tensor shaped C, T, H, W in [0, 1]."""

    video_path = Path(path)
    if not video_path.exists():
        raise FileNotFoundError(video_path)

    if isinstance(resize, int):
        resize_tuple: tuple[int, int] | None = (resize, resize)
    else:
        resize_tuple = resize

    try:
        return _read_video_with_cv2(video_path, max_frames=max_frames, resize=resize_tuple)
    except ImportError:
        return _read_video_with_imageio(video_path, max_frames=max_frames, resize=resize_tuple)


class PairedVideoDataset(Dataset):
    """Dataset of Stage-1 input videos paired with VEnhancer n30 pseudo-targets."""

    def __init__(
        self,
        stage1_dir: str | Path = ROOT / "outputs" / "normalized" / "stage1",
        target_dir: str | Path = ROOT / "outputs" / "normalized" / "v2v" / "venhancer_n30",
        scenes: tuple[str, ...] | list[str] = DEFAULT_SCENES,
        train_size: int | tuple[int, int] | None = 128,
        max_frames: int | None = 32,
    ) -> None:
        self.stage1_dir = Path(stage1_dir)
        self.target_dir = Path(target_dir)
        self.scenes = list(scenes)
        self.train_size = train_size
        self.max_frames = max_frames

        self.pairs = [
            (scene, self.stage1_dir / f"{scene}.mp4", self.target_dir / f"{scene}.mp4")
            for scene in self.scenes
        ]
        missing = [
            str(path)
            for _, input_path, target_path in self.pairs
            for path in (input_path, target_path)
            if not path.exists()
        ]
        if missing:
            raise FileNotFoundError("Missing paired video files:\n" + "\n".join(missing))

    def __len__(self) -> int:
        return len(self.pairs)

    def __getitem__(self, index: int) -> dict[str, object]:
        scene, input_path, target_path = self.pairs[index]
        input_video = read_video_tensor(input_path, max_frames=self.max_frames, resize=self.train_size)
        target_video = read_video_tensor(target_path, max_frames=self.max_frames, resize=self.train_size)

        frames = min(input_video.shape[1], target_video.shape[1])
        input_video = input_video[:, :frames]
        target_video = target_video[:, :frames]

        return {
            "scene": scene,
            "input": input_video,
            "target": target_video,
            "input_path": str(input_path),
            "target_path": str(target_path),
        }
