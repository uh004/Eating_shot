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

## plan 2.1.1

1. create the databases from plan 2.1
2. gomin on 'webapp'
    1. import the functions and classes from 'ai_workload'
    2. separate module for shared functions
    3. diango signals
    4. a service layer
    5. ???
    6. i should experiment by using git branches i guess
    7. no wait just do what i planned in keep

went for approach number 1: import the functions and classes from 'ai_workload'

## plan 2.2

1. what should i do next?
2. hardening the website!
    1. [x] edit and delete 운동 기록
    2. edit and delete 혈압
    3. edit and delete 혈당
    4. HOW???

#### plan 2.2.1

1. hardening the webapp
    2. [ ] edit and delete 운동 기록
    3. [ ] edit and delete 혈압
    4. [ ] edit and delete 혈당
    5. [ ] edit and delete 당화혈색소
    6. ...

## plan 3

1. implement ai related stuff
    1. ???
2. dockerize stuff
    1. add service and build to 2 folders: django app and api server for ai
    2. added logging stack (elk)
    3. ~~added monitoring stack (prometheus, grafana)~~
    4. ???
    5. TODO: SSL everything

## plan 개입.1

### deploying

### storage and database

#### firebase

oh crap. not supported.

I think it is better to use a cloud service for this.

since cloud service is expensive, it may be better off to use a local storage and sqlite3.

no wait i can do free postgresql with supabase!

thinking of supabase, it actually is a firebase alternative. and it provides stuff for storage and database.

instead of boto3, i can use the supabase python sdk.
django-storage?

#### monitoring(not enabled yet)

- prometheus
- grafana

#### logging

- elk stack
- ???

#### ci/cd

- github actions

##### deployment destination

- aws ec2 (https://aws.amazon.com/ec2/instance-types/)
    - instance type: arm64 or x86?
- gcp compute engine ($300 free credit)

may be better off sticking with one cloud provider.

## plan 3.2 (do this before doing all the money involving stuff in plan 3.1)

0. use environment variables for secrets
1. vulnerabilities (thinking about something to exploit when money is applied)
    1. image upload
        1. (excluding the malware scanning and the like)
        2. infinitity problem
            1. upload size
            2. upload count
    2. ???

### passwords to copy yada yada

```shell
=??uQq9qEjChT?8
```

