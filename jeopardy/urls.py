"""jeopardy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, patterns, url
from django.views.generic import TemplateView

from django.contrib import admin
from jeopardy.views import *


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name="index"),
    url(r'^(?P<id>\d+)/$', GameView.as_view(), name='game'),
    url(r'^(?P<id>\d+)/board$', BoardView.as_view(), name='board'),
    url(r'^(?P<id>\d+)/reset$', ResetView.as_view(), name='reset'),
    url(r'^(?P<game_id>\d+)/(?P<answer_id>\d+)$', AnswerView.as_view(), name='answer'),
    url(r'^(?P<game_id>\d+)/(?P<answer_id>\d+)/(?P<team_id>\d+)/$', TeamSelectedAnswerView.as_view(), name='select_team'),
    url(r'^(?P<game_id>\d+)/(?P<answer_id>\d+)/(?P<team_id>\d+)/wrong/$', WrongAnswerView.as_view(), name='answer_wrong'),
    url(r'^(?P<game_id>\d+)/(?P<answer_id>\d+)/(?P<team_id>\d+)/correct/$', CorrectAnswerView.as_view(), name='answer_correct'),
]
