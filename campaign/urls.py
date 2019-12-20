from django.urls import path
from . import views

app_name = 'campaign'
urlpatterns = [
    # Authentication
    path('list/', views.CampaignListView.as_view(), name='list_campaign'),
    path('detail/<int:pk>', views.detail_campaign_view, name='detail_campaign'),
    path('update/<int:pk>', views.CampaignUpdateView.as_view(), name='update_campaign'),
    path('delete/<int:pk>', views.delete_campaign_view, name='delete_campaign'),
    path('create/', views.CampaignCreateView.as_view(), name='create_campaign')
    
]
