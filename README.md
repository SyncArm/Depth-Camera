# Depth_Camera

**MPU**: Raspberry Pi 5 (Broadcom BCM2712 Quad-core Cortex-A76 (2.4GHz))

**카메라**: OV5647 x 2

- 초점 거리(f): 3.51mm
- 시야각(Alpha): 54도
- 카메라 간 거리(Baseline): 5.5cm
_________
### 버전 정보
- Python 3.11.2
- NumPy 1.24.2
- PySerial 3.5
- OpenCV 4.6.0
- MediaPipe 0.10.18
_________
### 실행방법
**Step0. python 가상환경 활성화**

- ```source <가상환경 위치>/bin/activate```
<br />

**Step1. 카메라 2대를 이용해서 카메라간 고정된 상태에서 동시에 사진촬영 진행**

- 실행: ```python take_picture.py```
- data/image_0, data/image_1에 각각의 카메라 촬영 사진이 저장됨
- 해상도: 960x960, 캘리브레이션을 위해 각각 20장 이상의 사진 촬영 권장
<br />

**Step2. 단일 카메라 캘리브레이션 및 스테레오 캘리브레이션 진행**

- 실행: ```python stereo_calibration.py```
- data 디렉터리에 캘리브레이션 결과값인 stereoMap.xml이 생성
<br />

**Step3. 캘리브레이션 값 및 삼각측량을 이용해 카메라에서 손까지의 거리를 추정**

- 실행: ```python depth_estimation.py```
- depth_estimation.py, triangulation.py, calibration.py가 같은 디렉터리 내에 존재해야함
- 카메라를 통해 깊이 추정 수행, 손의 (x픽셀 평균 좌표, y픽셀 평균 좌표, depth) 구한 후 UART를 통해 송신
- BaudRate: 115200


_________
### 디렉터리 구조

```
.
├── data
│ ├── image_0
│ ├── image_1
│ └── stereoMap.xml
│
├── step1_take_picture
│ └── take_picture.py
│
├── step2_stereo_calibration
│ └── stereo_calibration.py
│
└── step3_depth_estimation
  ├── calibration.py
  ├── depth_estimation.py
  └── triangulation.py
```
_________
### 아키텍처/회로
**Robot_Arm** : [GitHub 링크](https://github.com/SyncArm/Robot-Arm)
![image](https://github.com/user-attachments/assets/aec00e42-ab18-48f1-97a4-01285fe98365)
![image](https://github.com/user-attachments/assets/f158f253-86dd-4451-951b-64f692c40e9e)
_________
### 작동모습
![실행](https://github.com/user-attachments/assets/b90cdbf0-2e3d-49c6-acee-6df9555d9f5f)

