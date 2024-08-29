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

## changes

1. separated api, users, ai_workload and webapp

## plan 2

2. create app 'ai_workload'
    1. create model for ai workload queue. yes
    1. Kafka.
    2. separate server from app ai_workload. yes

## plan 3

1. implement ai related stuff
    1. ???
2. dockerize stuff

### passwords to copy yada yada

```shell
=??uQq9qEjChT?8
```

used djangorestframework_simplejwt instead of just pyjwt and the large amount of work
