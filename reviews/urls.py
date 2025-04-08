from django.urls import path
from . import views

urlpatterns = [
    path('add-review/<int:ride_id>/<int:reviewed_user_id>/', views.add_review, name='add_review'),
    path('view-reviews/<int:reviewed_user_id>/', views.view_reviews, name='view_reviews'),
    path('view-written-reviews', views.view_written_reviews, name='view_written_reviews'),
]