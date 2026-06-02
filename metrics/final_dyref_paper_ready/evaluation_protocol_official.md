# 공식 벤치마크 평가 프로토콜

본 평가는 DyRefHead의 결과를 기존 proxy 지표만으로 해석하지 않기 위해, 공식 또는 널리 사용되는 video evaluation benchmark를 함께 사용한다. VBench와 DOVER는 생성/비디오 품질을 평가하는 recognized video quality metric으로 사용한다. VE-Bench QA는 실행 가능한 경우에만 source-refined relation을 보는 보조 지표로 사용하며, 원래 text-driven video editing 평가용이므로 물리 보존의 주 근거로 사용하지 않는다.

Flow EPE와 Flow Mag Ratio는 기존과 동일하게 task-specific Stage-1 dynamics preservation proxy로 유지한다. 이 두 지표는 Stage-1 출력과 refinement 결과 사이의 optical-flow 기반 차이를 측정하지만, true physical correctness를 증명하는 지표는 아니다.

모든 target video는 benchmark 내부 resizing을 제외하면 normalized 256x256, 16 fps, 4 s 설정의 기존 결과물을 사용했다. RealWonder, VEnhancer, DyRefHead training 또는 video generation은 다시 실행하지 않았다.

사용한 benchmark version은 다음과 같다.

- VBench commit: `45e79ec14e69a2187202c675d2dbce1a71843d53`
- DOVER commit: `f1ddc96215bc7fbcf8f315c65d47905f339c3419`
- VE-Bench commit: `692faa944e6215c1a032cdd350c2d15d48a15156`; 공식 checkpoint 부재로 QA score는 산출하지 않음.
