# Previous Experiment Summary

## 역할

기존 `pipeline_ready` 결과는 더 이상 본 연구의 주 기여인 "후보 선택 파이프라인"으로 프레이밍하지 않는다. 대신 Frozen I2V backbone에 부착될 output refinement head의 필요성을 보여주는 pilot evidence로 사용한다.

## 핵심 관찰

기존 RealWonder Stage-1 출력과 VEnhancer strength sweep은 출력단 refinement가 visual/detail proxy를 크게 개선할 수 있음을 보여주었다. 특히 `venhancer_n30`은 3개 scene 평균에서 Stage-1 baseline 대비 sharpness를 `198.99`에서 `559.55`로 증가시켰다.

동시에 refinement는 Stage-1 dynamics drift를 도입했다. `venhancer_n30`의 3-scene 평균 `mean_flow_epe`는 `0.2796`, `flow_mag_ratio`는 `4.6502`였다. 이는 출력 refinement가 시각적 품질을 개선하더라도 I2V backbone이 만든 Stage-1 dynamics를 완전히 유지하지는 않음을 보여준다.

더 강한 VEnhancer 설정인 `n50`, `n70`, `n100`, `n200`은 output-head strength ablation처럼 해석할 수 있다. 이 sweep은 refinement 강도 변화에 따라 visual gain과 dynamics drift가 함께 변한다는 점을 보여주는 예비 분석이다.

## 새 연구 방향으로의 연결

이 결과는 단순한 "I2V output + external V2V post-processing"의 성공 사례가 아니다. 오히려 frozen I2V backbone의 출력단에 부착되는 lightweight output refinement head가 Stage-1 dynamics preservation 제약을 명시적으로 가져야 함을 보여준다.

따라서 기존 `n30` 선택은 더 이상 메인 contribution이 아니다. 기존 결과의 역할은 다음과 같다.

- Output refinement가 sharpness를 높일 수 있음을 보여주는 pilot evidence.
- Refinement 강도가 커질수록 Stage-1 dynamics drift가 생길 수 있음을 보여주는 ablation evidence.
- Dynamics-preserving refinement objective가 필요한 이유를 정량적으로 뒷받침하는 예비 실험.

## 주의할 해석

Stage-1 output은 physical ground truth가 아니라 physics-induced motion prior이다. 기존 실험은 true physical correctness를 검증하지 않는다. 결과는 visual gain-dynamics drift trade-off를 분석하고, Frozen I2V Backbone + Dynamics-Preserving Output Refinement Head 연구 방향을 동기화하는 근거로 사용해야 한다.
