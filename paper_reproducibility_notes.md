# Paper Reproducibility Notes

이 문서는 논문 작성 및 저장소 정리를 위한 재현성 확인 메모이다. 새 실험 결과를 추가로 주장하기보다, 현재 저장소에 포함된 코드, 설정, metric 요약 파일을 해석할 때 필요한 기준을 정리하는 데 목적이 있다.

## Scope

- 본 저장소는 Image-to-Video 출력 이후의 output-space refinement를 다루는 proof-of-concept 실험을 포함한다.
- Stage-1 I2V 출력은 physical ground truth가 아니라 physics-induced motion prior로 해석한다.
- VEnhancer n30 결과는 pseudo visual target으로 사용되며, 실제 정답 영상으로 간주하지 않는다.
- Flow 기반 지표는 Stage-1 dynamics preservation을 보기 위한 보조 proxy이며 true physical correctness를 직접 측정하지 않는다.

## Reproducibility Checklist

1. 실험 설정은 `configs/` 아래 CSV 파일에 기록된 입력, 출력, method 이름을 기준으로 확인한다.
2. 학습 및 export 스크립트는 `model_head_prototype/` 아래 파일을 기준으로 추적한다.
3. metric 계산과 요약은 `scripts/`의 batch 실행 및 summarize 스크립트를 사용한다.
4. 최종 해석에는 `metrics/final_dyref_paper_ready/`와 `metrics/official_benchmarks_revision/`의 정리 문서를 우선 참고한다.
5. 큰 영상 파일, checkpoint, 임시 출력물은 Git tracking 대상이 아니므로 재현 시 경로와 파일 존재 여부를 별도로 확인한다.

## Interpretation Notes

- VBench Imaging 증가는 visual quality proxy의 개선으로 제한해서 해석한다.
- Flow EPE와 flow magnitude ratio는 Stage-1 motion prior에서 얼마나 벗어났는지를 보는 보조 지표이다.
- DyRefHead 결과는 visual gain-dynamics drift trade-off를 분석하기 위한 초기 검증 결과로 보는 것이 적절하다.
- 더 강한 일반화 주장을 위해서는 더 많은 scene, human or perceptual evaluation, 그리고 physics-sensitive benchmark가 필요하다.

## Maintenance Notes

- README의 수치나 주장 문구를 수정할 때는 `paper_limitations.md`와 claim safety 관련 문서를 함께 확인한다.
- 새 metric을 추가하는 경우, 해당 metric이 무엇을 측정하는지와 무엇을 측정하지 않는지를 명시한다.
- 새로운 output artifact를 만들더라도 대용량 파일은 `.gitignore` 정책에 맞춰 별도 보관한다.
