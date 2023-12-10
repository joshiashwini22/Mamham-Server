# urls.py
from django.urls import path
from .views import dish_list, dish_detail, dish_create, dish_edit, dish_delete

urlpatterns = [
    path('dish/', dish_list, name='dish_list'),
    path('dish/<int:pk>/', dish_detail, name='dish_detail'),
    path('dish/new/', dish_create, name='dish_create'),
    path('dish/<int:pk>/edit/', dish_edit, name='dish_edit'),
    path('dish/<int:pk>/delete/', dish_delete, name='dish_delete'),
]
