from django.db import models
from django.contrib.auth.models import AbstractUser
import json
from math import sin, cos, sqrt, atan2, radians


def calculateDistance(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    # print("Result:", distance)
    return distance


# Create your models here.
class User(AbstractUser):
    name = models.CharField(blank=True, max_length=250, default='')
    email = models.EmailField(blank=False, null=False, unique=True)
    avatar = models.ImageField(blank=True, default='')
    latitude = models.FloatField(blank=True, default=0)
    longitude = models.FloatField(blank=True, default=0)
    score = models.IntegerField(default=0)
    questions = models.ManyToManyField('Question', through='Answer')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_score(self):
        answers = self.answer_set.all()
        total_questions = Question.objects.count()
        score = 0
        for answer in answers:
            if answer.is_right:
                score = score + 5
        self.score = score
        # self.score = score / total_questions

    def is_in_location(self):   # check if current user is in 10km radius
        try:
            target_config = Config.objects.get_or_create(key="target_location")[0]
            target_location = json.loads(target_config.value)
            lat = target_location.get('lat', '0.0')
            lng = target_location.get('lng', '0.0')
        except Exception:
            lat = '0.0'
            lng = '0.0'
        lat = float(lat)
        lng = float(lng)
        dist = calculateDistance(lat, lng, self.latitude, self.longitude)
        return dist < 10

    def get_campaign_in_location(self):
        # find the campaign that are available in your location, even there is many campaing, it returns only one.
        campaigns = Campaign.objects.all()
        for campaign in campaigns:
            lat = campaign.latitude
            lng = campaign.longitude
            dist = calculateDistance(lat, lng, self.latitude, self.longitude)
            if dist < 10:   # if the distance is in 10 km
                return campaign
        return None



class Question(models.Model):
    question = models.CharField(max_length=250)
    # answer = models.CharField(max_length=250)  # represent the correct answer of question
    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def check_answer(self, answer):
        correct_answer = self.answer.strip().lower()
        user_answer = answer.strip().lower()
        return correct_answer == user_answer

    def __str__(self):
        if self.question == "":
            return "Question" + str(self.id)
        return (self.question[:30] + '..') if len(self.question) > 30 else self.question


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    answer = models.CharField(max_length=250)
    is_right = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'question']

    def __str__(self):
        return "Answer" + str(self.id)



class Config(models.Model):
    key = models.CharField(unique=True, max_length=250)
    value = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Campaign(models.Model):
    name = models.CharField(max_length=250)
    latitude = models.FloatField(blank=True, default=0)
    longitude = models.FloatField(blank=True, default=0)

    def __str__(self):
        return self.name
