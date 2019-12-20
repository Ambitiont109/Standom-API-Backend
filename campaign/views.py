from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from main.models import Campaign
# Create your views here.


class CampaignListView(LoginRequiredMixin, ListView):
    model = Campaign
    template_name = 'Campaign/list.html'
    context_object_name = 'campaigns'


class CampaignCreateView(LoginRequiredMixin, CreateView):
    template_name = 'Campaign/update.html'
    success_url = reverse_lazy('campaign:list_campaign')
    model = Campaign
    fields = '__all__'

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Campaign Added Succesfully')
        return super().form_valid(form)


class CampaignUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'Campaign/update.html'
    success_url = reverse_lazy('campaign:list_campaign')
    model = Campaign
    fields = '__all__'

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Campaign Updated Succesfully')
        return super().form_valid(form)


@login_required
def delete_campaign_view(request, pk):
    if request.method == 'POST':
        campaign = get_object_or_404(Campaign.objects.all(), pk=pk)
        campaign.delete()
        messages.add_message(request, messages.SUCCESS, 'Campaign Deleted Successfully')
        return redirect('campaign:list_campaign')


@login_required
def detail_campaign_view(request, pk):
    if request.method == 'GET':
        campaign = get_object_or_404(Campaign.objects.all(), pk=pk)
        return render(request, 'Campaign/detail.html', {'campaign': campaign})
