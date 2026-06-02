# DyRefHead v2/v3 비교 메모

## 실험 전제

Stage-1 비디오는 frozen I2V backbone에서 나온 physics-induced motion prior로 취급한다. 이는 물리적 ground truth가 아니다.

VEnhancer n30은 pseudo visual target으로만 사용한다. 즉, 더 선명한 시각적 방향을 주는 참조 신호이지, 실제 정답 비디오나 물리적으로 올바른 비디오라는 뜻은 아니다.

DyRefHead는 frozen I2V backbone 뒤에 붙는 trainable output refinement head이며, 이 실험은 proof-of-concept 수준의 작은 overfit ablation이다.

## v2 결과 요약

256x256 평가에서 v2의 평균 결과는 다음과 같다.

| method | mean_flow_epe | flow_mag_ratio | mean_sharpness |
|---|---:|---:|---:|
| stage1_baseline | 0.0000 | 1.0000 | 279.5409 |
| venhancer_n30 | 0.2782 | 3.4906 | 364.3567 |
| dyref_head_v2_e20_256 | 0.1883 | 1.6971 | 299.5439 |

v2는 Stage-1보다 sharpness를 개선했고, VEnhancer n30보다 mean Flow EPE와 flow_mag_ratio를 낮췄다. 다만 visual/detail gain은 VEnhancer n30보다 약했다.

## v3 결과 요약

v3는 v2와 같은 구조를 사용하되 loss weight만 바꾼 ablation이다.

- `lambda_visual=1.0`
- `lambda_edge=0.75`
- `lambda_temporal_delta=0.15`
- `lambda_identity=0.05`

256x256 평가에서 v3의 평균 결과는 다음과 같다.

| method | mean_flow_epe | flow_mag_ratio | mean_sharpness |
|---|---:|---:|---:|
| stage1_baseline | 0.0000 | 1.0000 | 279.5409 |
| venhancer_n30 | 0.2782 | 3.4906 | 364.3567 |
| dyref_head_v2_e20_256 | 0.1883 | 1.6971 | 299.5439 |
| dyref_head_v3_edge075_temp015_e20_256 | 0.1901 | 1.5899 | 287.8850 |

v3는 Stage-1보다 sharpness가 높지만, v2보다 sharpness가 낮다. 반면 flow_mag_ratio는 v2보다 1에 더 가까워졌다. mean Flow EPE는 v2보다 아주 약간 나빠졌지만, VEnhancer n30보다는 여전히 낮다.

## 질문별 판단

### v3가 v2보다 sharpness를 개선했는가?

아니다. v2의 mean_sharpness는 299.5439이고, v3는 287.8850이다. v3는 Stage-1 baseline보다는 높지만 v2보다 낮다.

### v3가 Flow EPE를 VEnhancer n30보다 낮게 유지했는가?

그렇다. v3 mean_flow_epe는 0.1901이고 VEnhancer n30은 0.2782이다. 따라서 이 proxy 기준에서는 v3가 VEnhancer n30보다 Stage-1 flow에서 덜 벗어난다.

### v3가 flow_mag_ratio를 VEnhancer n30보다 1에 가깝게 유지했는가?

그렇다. v3 flow_mag_ratio는 1.5899이고 VEnhancer n30은 3.4906이다. v3는 v2의 1.6971보다도 1에 조금 더 가깝다.

### v3가 v2보다 전체적으로 나은가?

명확히 더 낫다고 보기 어렵다. v3는 flow_mag_ratio에서 v2보다 낫지만, sharpness와 mean_flow_epe에서는 v2보다 나쁘다. 현재 연구 목표가 "시각적 detail을 개선하면서 drift를 VEnhancer보다 낮게 유지"하는 것이라면 v2가 더 균형 잡힌 결과다.

## 다음 단계 판단

1. 지금 멈추고 논문 proof-of-concept로 정리: 가능하다. v2는 Stage-1 대비 visual proxy를 개선하고 VEnhancer 대비 dynamics drift proxy를 낮추는 결과를 보였다. 단, 주장은 제한적으로 해야 한다.
2. 50 epochs 실행: 현재로서는 우선순위가 낮다. v3 ablation이 sharpness 개선으로 이어지지 않았기 때문에 단순 epoch 증가가 최선인지 확실하지 않다.
3. loss 재조정: 가장 합리적인 다음 실험이다. edge weight를 더 키우는 방향은 v3에서 기대만큼 작동하지 않았다. 대신 `lambda_edge=0.5`를 유지하고 visual target 쪽을 강화하거나, temporal_delta를 유지한 채 작은 perceptual/detail proxy를 추가하는 편이 낫다.
4. capacity 증가: 아직 필요하다고 단정하기 어렵다. 현재 v2가 이미 개선을 보였으므로, 먼저 loss 설계를 더 정리하는 것이 낫다.

## 결론

현재 기준에서는 v2를 대표 결과로 사용하는 것이 더 적절하다. v3는 dynamics magnitude ratio를 조금 더 안정화했지만, 핵심 약점이었던 visual/detail gain을 개선하지 못했다.

따라서 다음 액션은 50 epoch로 바로 늘리기보다, v2를 중심 proof-of-concept로 정리하고 필요한 경우 한 번 더 loss 설계를 조정하는 것이다. 이 실험만으로 true physical correctness나 완전한 dynamics preservation을 주장해서는 안 된다.
