from django.urls import path
from .views import UserList, UserDetail
# from .views import RegisterView, CustomLoginView
urlpatterns = [
    # path('register/', RegisterView.as_view(), name='register'),
    # path('login/', CustomLoginView.as_view(), name='login'),
    path('api/users/', UserList.as_view(), name='user-list'),
    path('api/users/<int:pk>/', UserDetail.as_view(), name='user-detail'),
]
