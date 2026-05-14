# Graph Coloring Timetable Generator

고교학점제 환경의 시간표 생성을 그래프 채색 문제로 모델링한 웹 애플리케이션입니다.

## 구성

- `backend`: FastAPI + Pandas + NetworkX
- `frontend`: React + Vite

## 핵심 아이디어

- 정점: 과목(또는 과목 그룹 단위 강좌)
- 간선: 동시 배치 불가 충돌
  - 동일 교사
  - 동일 교실
  - 동일 그룹
  - 공통 수강 학생 존재
- 색: 시간대
- 채색수: 필요한 최소 시간대 수

## 입력 파일 형식

- 지원 확장자: `.xlsx`, `.xls`, `.csv`
- 필수 컬럼(대소문자 무관):

- `course_id`
- `course_name`
- `group_id`
- `teacher`
- `room`
- `credit`
- `students` (`학번1,학번2,...`)

## 실행

### 1) Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 Vite 주소(보통 `http://localhost:5173`)에 접속 후 Excel 업로드.

샘플 데이터: `samples/sample_courses.csv`

## 생성 결과

- 시간대별 과목 배치
- 학생별 개인 시간표
- 교사별 개인 시간표
