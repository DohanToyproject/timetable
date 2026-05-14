# Backend (FastAPI)

## Run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## API

- `GET /health`
- `POST /api/generate`
  - form-data:
    - `file`: `.xlsx` | `.xls` | `.csv`
    - `algorithm`: `greedy` | `welsh_powell`
    - `days`: number of days (default 5)

## Input columns

Required headers (case-insensitive):

- `course_id`
- `course_name`
- `group_id`
- `teacher`
- `room`
- `credit`
- `students` (comma-separated student ids)
