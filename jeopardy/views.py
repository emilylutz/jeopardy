from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, render_to_response
from django.views.generic import ListView, View, TemplateView
from django.views.generic.edit import FormView, UpdateView

from jeopardy.models import Game, Team, Column, Answer


class BoardView(TemplateView):
    """
    View all questions.
    """
    template_name = 'board.html'

    def get(self, request, *args, **kwargs):
        try:
            self.game = Game.objects.get(id=kwargs['id'])
        except Game.DoesNotExist:
            raise Http404("Game with given id does not exist")
        return super(BoardView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BoardView, self).get_context_data(**kwargs)
        context.update({
            'game': self.game,
            # 'logged_in': logged_in,
            # 'user': self.request.user,
            # 'form': form,
            # 'project_reviews': project_reviews,
            # 'own_reviews': own_reviews,
            # 'num_reviews': num_reviews,
            # 'bookmarked': bookmarked
        })
        return context