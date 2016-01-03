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
        num_cols = len(self.game.columns.all())
        num_rows = len(self.game.columns.all()[0].answers.all())
        rows = [[None for i in range(num_cols)] for j in range(num_rows)]
        cur_column = 0
        for col in self.game.columns.all():
            for answer in col.answers.all():
                row = answer.row
                rows[answer.row][cur_column] = answer
                print str(answer.row) + ", " + str(cur_column) + ", " + answer.answer
                print rows
            cur_column += 1
        print rows
        context.update({
            'game': self.game,
            'rows': rows,
            # 'logged_in': logged_in,
            # 'user': self.request.user,
            # 'form': form,
            # 'project_reviews': project_reviews,
            # 'own_reviews': own_reviews,
            # 'num_reviews': num_reviews,
            # 'bookmarked': bookmarked
        })
        return context

class AnswerView(TemplateView):
    """
    View a specific answer.
    """
    template_name = 'answer.html'

    def get(self, request, *args, **kwargs):
        try:
            self.game = Game.objects.get(id=kwargs['game_id'])
        except Game.DoesNotExist:
            raise Http404("Game with given id does not exist")
        try:
            self.answer = Answer.objects.get(id=kwargs['answer_id'])
        except Answer.DoesNotExist:
            raise Http404("Answer with given id does not exist")
        return super(AnswerView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AnswerView, self).get_context_data(**kwargs)
        context.update({
            'game': self.game,
            'answer': self.answer,
            'teams': self.game.teams.all()
        })
        return context

class WrongAnswerView(TemplateView):
    """
    View a specific answer.
    """
    def get(self, request, *args, **kwargs):
        try:
            self.game = Game.objects.get(id=kwargs['game_id'])
        except Game.DoesNotExist:
            raise Http404("Game with given id does not exist")
        try:
            self.answer = Answer.objects.get(id=kwargs['answer_id'])
        except Answer.DoesNotExist:
            raise Http404("Answer with given id does not exist")
        try:
            self.team = Team.objects.get(id=kwargs['team_id'])
        except Answer.DoesNotExist:
            raise Http404("Team with given id does not exist")

        self.team.score = self.team.score - self.answer.value
        self.team.save()

        return redirect('answer', game_id=self.game.id, answer_id=self.answer.id)

class CorrectAnswerView(TemplateView):
    """
    View a specific answer.
    """
    template_name = 'correct_answer.html'

    def get(self, request, *args, **kwargs):
        try:
            self.game = Game.objects.get(id=kwargs['game_id'])
        except Game.DoesNotExist:
            raise Http404("Game with given id does not exist")
        try:
            self.answer = Answer.objects.get(id=kwargs['answer_id'])
        except Answer.DoesNotExist:
            raise Http404("Answer with given id does not exist")
        try:
            self.team = Team.objects.get(id=kwargs['team_id'])
        except Answer.DoesNotExist:
            raise Http404("Team with given id does not exist")

        self.team.score = self.team.score + self.answer.value
        self.team.save()

        self.answer.state = 1
        self.answer.save()

        return super(CorrectAnswerView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CorrectAnswerView, self).get_context_data(**kwargs)
        context.update({
            'game': self.game,
            'answer': self.answer,
        })
        return context

class TeamSelectedAnswerView(TemplateView):
    """
    View a specific answer.
    """
    template_name = 'team_selected.html'

    def get(self, request, *args, **kwargs):
        try:
            self.game = Game.objects.get(id=kwargs['game_id'])
        except Game.DoesNotExist:
            raise Http404("Game with given id does not exist")
        try:
            self.answer = Answer.objects.get(id=kwargs['answer_id'])
        except Answer.DoesNotExist:
            raise Http404("Answer with given id does not exist")
        try:
            self.team = Team.objects.get(id=kwargs['team_id'])
        except Answer.DoesNotExist:
            raise Http404("Team with given id does not exist")

        return super(TeamSelectedAnswerView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TeamSelectedAnswerView, self).get_context_data(**kwargs)
        context.update({
            'game': self.game,
            'answer': self.answer,
            'team': self.team
        })
        return context
