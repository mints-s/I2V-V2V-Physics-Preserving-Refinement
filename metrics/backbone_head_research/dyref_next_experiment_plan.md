# DyRefHead 다음 최소 실험 계획

## 실험 목적

이번 실험은 `DyRefHead`를 랜덤 텐서용 형태 검증 모듈에서, 실제 비디오 공간에서 학습 가능한 최소 출력 보정 헤드로 바꾸는 proof-of-concept이다. 입력은 frozen I2V backbone의 Stage-1 비디오이며, 헤드는 Stage-1 출력 위에 작은 residual 보정을 예측한다. 전체 I2V 모델을 다시 학습하지 않고, 출력단의 작은 3D convolution head만 학습한다.

이 실험은 완성된 모델이나 최종 방법론을 주장하기 위한 것이 아니다. 3개 장면에 대해 과적합이 가능한지, 그리고 시각적 보정이 Stage-1 동역학을 크게 훼손하지 않는 방향으로 유도될 수 있는지를 확인하는 최소 검증이다.

## VEnhancer n30의 역할

VEnhancer n30 결과는 ground-truth 비디오가 아니라 pseudo visual target이다. 즉, 더 선명하거나 시각적으로 정리된 방향을 제공하는 참조 신호로만 사용한다. VEnhancer가 만든 움직임이나 구조가 실제 물리 정답이라는 뜻은 아니며, 해당 결과를 그대로 물리적 기준으로 해석하면 안 된다.

따라서 학습 손실의 의미도 제한적으로 해석해야 한다. `visual_l1_loss(pred, target)`은 pseudo-target에 가까워지는 시각적 보정 신호이고, 실제 세계의 정답 프레임에 대한 supervised loss가 아니다.

## Stage-1의 역할

Stage-1 비디오는 frozen I2V backbone에서 나온 physics-induced motion prior로 취급한다. 여기서의 핵심 가정은 Stage-1이 장면의 기본 시간 흐름과 물체 운동 단서를 담고 있으며, DyRefHead는 이를 대체하기보다 보존하면서 시각적 품질을 보정해야 한다는 것이다.

그래서 `identity_first_frame_loss(pred, input)`과 `temporal_smoothness_loss(pred)`를 함께 사용한다. 첫 프레임 보존은 입력 조건과의 급격한 이탈을 줄이고, 시간 smoothness는 프레임 간 깜빡임을 줄이기 위한 약한 제약이다. optical flow 보존 손실은 아직 이 최소 실험에 포함하지 않으며, 추후 가벼운 flow estimator 또는 precomputed flow cache를 연결한 뒤 추가한다.

## 비교할 지표

세 방법을 같은 장면 3개에서 비교한다.

- `stage1_baseline`: frozen I2V backbone의 Stage-1 출력
- `venhancer_n30`: pseudo visual target으로 사용한 VEnhancer 결과
- `dyref_head`: Stage-1 입력 위에 DyRefHead를 적용한 출력

기존 metric pipeline을 사용해 flow preservation proxy와 video quality proxy를 비교한다. 해석의 중심은 DyRefHead가 VEnhancer n30의 시각적 장점을 일부 따라가면서도, Stage-1 대비 flow 변화가 과도하게 커지지 않는지에 둔다.

## 기여 가능성을 지지하는 결과

제안 방향을 지지하는 결과는 다음과 같다.

- `dyref_head`가 `stage1_baseline`보다 sharpness 등 시각 품질 proxy에서 개선된다.
- `dyref_head`의 flow preservation 지표가 `venhancer_n30`보다 Stage-1에 더 가깝다.
- 세 장면 모두에서 DyRefHead 출력이 Stage-1의 주요 움직임 구조를 유지하면서 pseudo-target 방향의 시각적 정리를 보인다.
- 과적합 실험 로그에서 visual loss가 감소하되, temporal 및 identity 관련 손실이 폭발하지 않는다.

이런 결과가 나오면 "frozen I2V backbone의 동역학 prior를 유지하면서 출력단 보정 헤드로 시각 품질을 개선할 수 있다"는 연구 방향을 제한적으로 뒷받침할 수 있다.

## 기여 가능성을 약화하는 결과

다음 결과는 제안 방향을 약화한다.

- `dyref_head`가 `venhancer_n30`을 단순 복사하려 하면서 Stage-1 대비 flow preservation이 크게 나빠진다.
- 시각 품질 proxy가 거의 개선되지 않거나, 오히려 blur/flicker가 증가한다.
- 3개 장면 과적합에서도 loss가 안정적으로 줄지 않는다.
- 첫 프레임 또는 주요 물체 위치가 Stage-1에서 크게 벗어나, dynamics prior 보존이라는 목적과 충돌한다.

이 경우 DyRefHead 구조, 손실 가중치, flow preservation loss, 또는 pseudo-target 사용 방식 자체를 다시 설계해야 한다. 특히 이 실험만으로 true physical correctness를 주장할 수 없으며, 이후 실제 물리 평가나 더 강한 dynamics consistency 검증이 필요하다.
