# Depth_Camera

__MPU__: Raspberry Pi 5 (Broadcom BCM2712 Quad-core Cortex-A76 (2.4GHz))
<br />
__카메라__: OV5647 x 2 
<br />
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

- source <가상환경 이름>/bin/activate
<br />

**Step1. 카메라 2대를 이용해서 카메라간 고정된 상태에서 동시에 사진촬영 진행**

- 실행: python take_picture.py
- data/image_0, data/image_1에 각각의 카메라 촬영 사진이 저장됨
- 해상도: 960x960, 캘리브레이션을 위해 각각 20장 이상의 사진 촬영 권장
<br />

**Step2. 단일 카메라 캘리브레이션 및 스테레오 캘리브레이션 진행**

- 실행: python stereo_calibration.py
- data 디렉터리에 캘리브레이션 결과값인 stereoMap.xml이 생성
<br />

**Step3. 캘리브레이션 값 및 삼각측량을 이용해 카메라에서 손까지의 거리를 추정**

- 실행: python depth_estimation.py
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
![image](https://github.com/user-attachments/assets/aec00e42-ab18-48f1-97a4-01285fe98365)
![image](https://github.com/user-attachments/assets/f158f253-86dd-4451-951b-64f692c40e9e)
_________
### 부품 리스트

- 로봇암 프레임: https://www.devicemart.co.kr/goods/view?no=15475211<br />
- 라즈베리파이5: https://www.devicemart.co.kr/goods/view?no=15215450<br />
- 아두이노 레오나르도도: https://www.devicemart.co.kr/goods/view?no=1278923<br />
- 서보모터 드라이버: https://www.devicemart.co.kr/goods/view?no=15526350<br />
- 서보모터: https://www.devicemart.co.kr/goods/view?no=1313388<br />
- OV5647: https://www.devicemart.co.kr/goods/view?no=10824332<br />
- 카메라 리본 케이블 2개: https://www.devicemart.co.kr/goods/view?no=15289286<br />
- 5V 2A 어답터: https://www.devicemart.co.kr/goods/view?no=10921172<br />
- 라즈베리파이 어답터: https://www.devicemart.co.kr/goods/view?no=15502416<br />
- USB A to Micro B: https://www.devicemart.co.kr/goods/view?no=1061716<br />
- 점퍼 케이블 (M/F): https://www.devicemart.co.kr/goods/view?no=1321195<br />
_________
### 참고 자료
- 깊이 측정을 위한 커스텀 임베디드 스테레오 시스템
http://www.fainstec.com/main/sub.asp?cate=&ptab=02&page2=22&avan=1004020000&FAINSTEC_applicationNoteMode=view&intseq=67&RD=900UKL6SPI&
- 라즈베리파이5 카메라 사용 및 OpenCV 카메라 캘리브레이션
https://blog.naver.com/idea_robot/223469882209
- 라즈베리파이에서 OpenCV 사용하기
https://velog.io/@gemnsh/라즈베리파이에서-OpenCV-사용하기
- Depth Estimation with OpenCV Python for 3D Object Detection
https://youtu.be/uKDAVcSaNZA?feature=sharedComputerVision


