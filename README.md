# Eating_shot

당뇨병 환자를 대상으로 한 건강 관리 서비스

## 명령어

- `poetry install` : 프로젝트 요구사항 설치
- `./manage.py makemigrations ai_workload users` : 마이그레이션 파일 생성
- `./manage.py migrate` : 마이그레이션 적용
- `python manage.py runserver` : 서버 실행
- `docker compose up -d` : 카프카
- `python -m run_consumer` : 카프카 먹기 시작
- `python -m inference_dummy_fastapi.main` : fastapi 서버 시작하기

### ~~(fastapi 서버 디렉토리에서)~~

- ~~`uvicorn main:app --port 8099 --reload` : fastapi 서버 시작하기~~

## url

- ~~`http://localhost:8000/admin/` : 관리자 페이지~~
- `http://localhost:8000/docs` : swagger 페이지
- `http://localhost:8000/redoc` : redoc 페이지
- `http://localhost:8000/schema` : schema 파일

