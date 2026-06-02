# Reframed Korean Abstract

Image-to-Video(I2V) 모델은 입력 이미지와 텍스트 조건으로부터 시간적 동역학을 생성할 수 있지만, Stage-1 출력은 공간적 디테일이나 시간적 안정성 측면에서 제한적일 수 있다. 출력 refinement는 이러한 품질을 개선할 수 있으나, 동시에 I2V backbone이 생성한 motion prior를 변경하여 Stage-1 dynamics drift를 유발할 수 있다.

본 연구는 frozen I2V backbone에 lightweight dynamics-preserving output refinement head를 부착하는 방향을 제안한다. Stage-1 출력은 physical ground truth가 아니라 physics-induced motion prior로 취급하며, refinement head는 visual/spatio-temporal quality를 개선하면서 Stage-1 dynamics preservation을 명시적으로 고려하도록 설계된다. 이를 위해 visual gain과 dynamics drift를 함께 평가하고, Stage-1 optical flow 또는 motion prior를 이용한 dynamics-preserving refinement objective를 정의한다.

Pilot experiment로 RealWonder Stage-1 출력과 VEnhancer strength sweep을 분석한 결과, output refinement는 3개 scene 평균 sharpness를 `198.99`에서 `559.55`로 증가시켰지만, 선택된 `venhancer_n30`에서도 `mean_flow_epe=0.2796`, `flow_mag_ratio=4.6502`의 non-zero dynamics drift가 관찰되었다. 이는 단순한 외부 V2V enhancement나 upscaling이 아니라, frozen I2V backbone의 Stage-1 dynamics를 보존하도록 제약된 output refinement head 설계가 필요함을 시사한다. 본 초록은 trainable head의 완성된 성능을 주장하지 않으며, 현재 결과는 dynamics-preserving output head 설계를 동기화하는 예비 근거로 사용된다.
