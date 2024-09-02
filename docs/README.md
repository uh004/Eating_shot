## plan

1. create app 'user'
    1. create the models for users by leveraging apis from Django
    2. create files for app 'user'
        1. forms.py
        2. serializers.py
        3. urls.py
    3. create api related files for app 'user'
        1. api_urls.py
        2. api_views.py
    4. create tests
2. create app 'ai_workload'
    1. create model for ai workload queue?
    1. Kafka or RMQ?
    2. separate server from app ai_workload?
    3. implement ai related stuff
    4. ???
3. dockerize (with cuda enabled)
4. ???

## plan 1.5

1. separated api, users, ai_workload and webapp

## plan 2

2. create app 'ai_workload'
    1. create model for ai workload queue. done
    1. Kafka. done
    2. separate server from app ai_workload. done

used djangorestframework_simplejwt instead of just pyjwt and the large amount of work

## plan 2.1

1. according to these newly created pages:
    - databases
        1. 누적 칼로리(탄, 단, 지)
        2. 누적 운동기록들
            - 운동시간
        3. 당뇨 지표
            4. 혈압: 년월일, 수축기, 이완기 (실제 건강 기준: 위험, 경계, 정상)
            5. 혈당: 년월일, 아침, 점심, 저녁 (식전/식후), 공복
            6. 당화혈색소: 년월일, 당화혈색소(%)
        4. 식단기록(이미지 업로드): 년월일, (아침,점심,저녁,간식), (칼로리, 탄수화물, 단백질, 지방)

        - 일일 뽑아내기 / 주간 뽑아내기
        - 전체 유저의 상위 n%입니다 표식
2. integrate the new databases with the existing ones
3. ???
4. Profit

## plan 3

1. implement ai related stuff
    1. ???
2. dockerize stuff

### passwords to copy yada yada

```shell
=??uQq9qEjChT?8
```

