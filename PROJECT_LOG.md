# Visualization of Sudden Unintended Acceleration (SUA) Accident Data

---

## 🚀 Project Overview
이 프로젝트는 단순히 데이터를 시각화하는 것을 넘어, **사회적 문제인 자동차 급발진 사고의 심각성을 대중에게 알리고, 데이터 기반의 통찰을 제공하기 위한 저의 시도**입니다.

2024 중순부터 연이어 보도되는 급발진 사고 뉴스 기사들을 접하면서, 이 문제가 생각보다 훨씬 빈번하고 심각하게 발생하고 있음을 느꼈습니다. 특히, 급발진의 명확한 정의나 원인 규명이 어려워 자동차 제조사로부터 적절한 보상을 받지 못하고, 심지어 아무 잘못 없이 소중한 생명을 잃는 안타까운 사례들이 저를 움직이게 했습니다.

관련 뉴스들을 살펴보며 나이, 차종 등 특정 조건에 따라 사고 양상이 미묘하게 다르다는 점에 주목했고, **이러한 파편화된 정보들을 체계적으로 수집하고 시각화한다면 급발진 사고의 패턴을 이해하고, 나아가 '왜 이런 사고가 일어나는가'에 대한 작은 실마리라도 제공할 수 있지 않을까** 하는 희망을 품게 되었습니다.

비록 제가 평범한 대학생이고 이 프로젝트가 얼마나 많은 사람들에게 도달할지는 알 수 없지만, 저의 최종 결과물이 대중에게 **"급발진 사고가 단순한 해프닝이 아니라 심각한 사회 문제이며, 많은 사람들이 그 피해를 받고 있구나"** 라는 인식을 심어줄 수 있기를 진심으로 바랍니다. 데이터 시각화를 통해 이 중요한 메시지를 전달하고, 궁극적으로는 이 문제에 대한 사회적 관심을 높이는 데 기여하고자 합니다.<br><br>


This project goes beyond simply visualizing data—it is my attempt to raise public awareness about the seriousness of sudden unintended acceleration (SUA) incidents, a significant social issue, and to provide data-driven insights.

Since the middle of 2024, I have come across a series of news articles reporting SUA accidents, which made me realize that these incidents occur far more frequently and seriously than I had previously thought. In particular, I was moved by the heartbreaking cases where victims lost their lives or failed to receive proper compensation from car manufacturers due to the lack of a clear definition or explanation for SUA.

While reviewing related news, I noticed that the patterns of these accidents subtly differ depending on factors such as age and vehicle model. This led me to believe that systematically collecting and visualizing this fragmented information could help us better understand the patterns of SUA incidents and perhaps even provide some clues as to why they occur.

Although I am just an ordinary university student and cannot predict how many people this project will reach, I sincerely hope that my work will help the public recognize that SUA accidents are not just isolated incidents, but a serious social problem affecting many people. Through data visualization, my goal is to convey this important message and ultimately contribute to raising social awareness about this issue.

---

## 🗓️ Project Timeline & Progress (프로젝트 타임라인 및 진행 상황)

### Phase 1: Data Acquisition & Preprocessing (데이터 수집 및 전처리)
- **목표**: 급발진 사고 관련 뉴스 기사 데이터 확보 및 정제
- **진행 상황**: Selenium을 활용한 웹 크롤링 스크립트 개발 예정. 뉴스 기사 내의 사고 발생 시간, 장소, 차량 정보, 피해 내용 등 핵심 정보 추출 및 정규화 작업 계획 중.
- **마일스톤**: 초기 데이터셋 1차 수집 및 JSON 형식 저장 완료

### Phase 2: Data Storage & Management (데이터 저장 및 관리)
- **목표**: 정제된 데이터를 효율적으로 저장하고 관리할 수 있는 시스템 구축
- **진행 상황**: JSON 형식으로 수집된 데이터를 체계적으로 구조화하고 관리하는 작업 계획 중
- **마일스톤**: JSON 데이터 구조 확정 및 데이터 저장 완료

### Phase 3: Data Processing & Analysis (데이터 처리 및 분석)
- **목표**: 프론트엔드 시각화 도구(D3.js)에서 활용할 수 있도록 데이터 가공
- **진행 상황**: JSON 데이터를 D3.js가 필요로 하는 형태로 변환하고 처리하는 로직 개발 예정
- **마일스톤**: 핵심 데이터 처리 로직 구현 완료

### Phase 4: Data Visualization Implementation (데이터 시각화 구현)
- **목표**: 수집 및 정제된 데이터를 활용하여 사용자 친화적인 시각화 대시보드 개발
- **진행 상황**: D3.js를 사용하여 다양한 시각화 차트 (예: Bar Chart, Radar Chart, Bubble Chart, Donut Chart, Heatmap 등) 구현 예정. 사용자가 데이터를 필터링하고 상호작용할 수 있도록 인터랙티브 기능 추가 계획 중
- **마일스톤**: 주요 시각화 차트 프로토타입 구현 완료

---

## 🛠️ Technologies Used (사용 기술)
- **Data Collection & Preprocessing:** Python, Selenium
- **Data Storage:** JSON
- **Data Processing & Analysis:** Python
- **Frontend & Visualization:** HTML, CSS, JavaScript, D3.js
- **Version Control:** Git, GitHub

---

## ✨ Key Features & Functionality (주요 기능) [예정]
* **다양한 시각화 차트**:
    * **Bar Chart**: 급발진 사고 발생 빈도 (연령대별, 차량 모델별 등)
    * **Radar Chart**: 사고 발생 시 환경 요인 (날씨, 도로 상태 등) 분석
    * **Bubble Chart**: 사고 위치 및 피해 규모 (위치, 피해 정도 등)
    * **Donut Chart**: 특정 사고 요인 (급발진 의심 원인 등) 비율
    * **Heatmap**: 사고 다발 지역 및 시간대 패턴 분석
* **인터랙티브 대시보드**: 사용자가 원하는 조건 (예: 특정 연도, 특정 제조사)으로 데이터를 필터링하고 시각화된 결과를 실시간으로 확인할 수 있는 기능
* **데이터 원본 표시**: 시각화된 데이터의 출처(뉴스 기사 링크 등)를 함께 제공하여 신뢰성 확보

---

## 💡 Development Process & Challenges (개발 과정 및 직면했던 문제)


---

## 🌱 Lessons Learned & Future Enhancements (배운 점 및 향후 개선 계획)


---

## 🔗 Live Demo / Screenshots / Video (Optional)


---

## 🤝 Contribution & Contact
* **Email:** [ekbin93@naver.com / ekbin93@gmail.com]
* **GitHub Profile:** [https://github.com/myoungse]
