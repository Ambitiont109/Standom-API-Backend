from django.urls import path
from . import views

app_name = 'question'
urlpatterns = [
    # Authentication
    # path('list/', views.CampaignListView.as_view(), name='list_campaign'),
    # path('detail/<int:pk>', views.detail_campaign_view, name='detail_campaign'),
    # path('update/<int:pk>', views.CampaignUpdateView.as_view(), name='update_campaign'),
    # path('delete/<int:pk>', views.delete_campaign_view, name='delete_campaign'),
    # path('create/', views.CampaignCreateView.as_view(), name='create_campaign')
    path('create/<int:campaign_pk>', views.add_question_view, name='create_question'),
    path('edit/<int:question_pk>', views.edit_question_view, name='edit_question'),
    path('delete/<int:campaign_pk>/<int:question_pk>', views.delete_question_view, name='delete_question')
]
