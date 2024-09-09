# Eating_shot

당뇨병 환자를 대상으로 한 건강 관리 서비스

## 명령어 (윈도 리눅스 맥 모두)

젯브레인계열에서 프로젝트 파일이 안 뜨면 invalidate cache and restart 하면 해결됨 왜 그런지 모르겠음

- `poetry install` : 프로젝트 요구사항 설치 (윈도우 한정 3.12로는 안되는 듯 하고, 3.11, 3.10 로는 잘 되는 것을 확인)
- `python manage.py makemigrations ai_workload users` : (없으면) 마이그레이션 생성
- `python manage.py migrate` : 마이그레이션 적용
- `python manage.py runserver` : 서버 실행

## 명령어 (도커)

- `docker compose up -d` : 전부 실행 (파일이 바뀌었을 시 `--build` 옵션을 붙이면 됨) 30초 정도 걸림.
- `docker compose up [서비스 이름 (공백으로 복수 서비스 기입 가능)]` : 서비스들 실행
- `docker compose down` : 전부 종료 (-v 옵션을 붙이면 볼륨도 삭제). 재시작(`--force-recreate` 등) 시 kafka가 자기 자기를 지우지 못하고 재시작되니 주의.


- ~~- `docker compose up -d` : 카프카~~
- ~~- `python -m run_consumer` : 카프카 먹기 시작~~
- ~~- `python -m inference_dummy_fastapi.main` : 간이 서버 시작~~

### ~~(fastapi 서버 디렉토리에서)~~

- ~~`uvicorn main:app --port 8099 --reload` : fastapi 서버 시작하기~~

## url

(docker-compose로 실행시 포트 없음)

- ~~`http://localhost:8000/admin/` : 관리자 페이지~~
- `http://localhost:8000/docs` : swagger 페이지
- `http://localhost:8000/redoc` : redoc 페이지
- `http://localhost:8000/schema` : schema 파일

- `http://localhost:5601` : kibana

^ 8기가 램으론부족한듯 함

최신버전으로 업데이트하니 토큰방식 로그인같은걸 요구함. 절차를 잘 따라주면 됨 배포할때 참고...

elasticsearch 컨테이너로 가서 `bin/elasticsearch-reset-password auto [-u <유저네임>]` 입력해서 비밀번호 설정 해야함..

^ 이걸 다시 .env에 넣어놓고 셋업 완료해야 함.

가동될때까지 노트북에서 70초, 성능좋은 데탑에서 30초정도 걸림

#### query dsl

```json
{
  "query": {
    "bool": {
      "should": [
        {
          "match_phrase": {
            "container.name": "inference_app"
          }
        },
        {
          "match_phrase": {
            "container.name": "django_app"
          }
        },
        {
          "match_phrase": {
            "container.name": "kafka_consumer"
          }
        },
        {
          "match_phrase": {
            "container.name": "nginx"
          }
        }
      ],
      "minimum_should_match": 1
    }
  }
}
```
