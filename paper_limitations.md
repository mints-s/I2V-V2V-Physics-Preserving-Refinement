# Limitations

## 1. 실험 Scene 수의 제한

본 실험은 `scene01`, `scene02`, `scene03`의 3개 scene에 기반한다. 따라서 결과는 proof-of-concept로 해석해야 하며, 다양한 물체, 접촉 조건, 카메라 움직임, 장면 복잡도에 대한 일반화 성능을 충분히 보여주지는 않는다.

## 2. Pseudo-Target의 한계

VEnhancer n30은 pseudo visual target으로 사용되었으며 ground truth가 아니다. VEnhancer 출력은 더 높은 visual detail을 제공할 수 있지만, 실제 물리적으로 올바른 motion이나 appearance를 보장하지 않는다. 따라서 DyRefHead가 VEnhancer n30에 가까워지는 것은 ground-truth supervised learning과 다르다.

## 3. Flow Metric의 해석 한계

본 논문에서 사용하는 flow 기반 metric은 Stage-1 dynamics preservation proxy이다. 즉, refined video가 Stage-1 motion prior에서 얼마나 벗어나는지를 측정하는 데 사용된다. 이 값은 physical correctness 자체를 측정하지 않으며, 실제 물리 법칙을 만족하는지 판단하는 지표가 아니다.

## 4. Video-Space Proof-of-Concept

DyRefHead는 RGB video-space output refinement head이다. 현재 구조는 frozen I2V backbone의 latent representation이나 denoising trajectory 내부에 통합되지 않았다. 따라서 backbone 내부 생성 과정 자체를 제어하는 방법과는 다르며, output-side post-refinement에 가까운 proof-of-concept이다.

## 5. Perceptual 및 Human Evaluation 부재

현재 결과는 mean sharpness, flow EPE, flow magnitude ratio와 같은 proxy metric 중심으로 평가되었다. 실제 사용자가 인식하는 시각적 품질, temporal naturalness, physics-sensitive plausibility에 대한 human study나 perceptual evaluation은 아직 수행되지 않았다.

## 6. True Physical Correctness를 주장하지 않음

Stage-1은 physics-induced motion prior일 뿐 physical ground truth가 아니다. VEnhancer n30도 ground-truth target이 아니다. 따라서 본 연구는 true physical correctness, perfect preservation, globally optimal refinement를 주장하지 않는다.

## 7. 향후 과제

향후 연구에서는 더 많은 scene에 대한 평가, human/perceptual study, explicit flow 또는 trajectory preservation objective, latent-space 또는 diffusion-step-level integration, 더 정교한 visual detail loss를 검토해야 한다.
