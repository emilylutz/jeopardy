from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, render_to_response
from django.views.generic import ListView, View, TemplateView
from django.views.generic.edit import FormView, UpdateView

from jeopardy.models import Game, Team, Column, Answer

from _ssl import SSLError
import urllib2, urllib, json, time, re, threading

DEBUG_LEVEL = 0  # Set this to 1 to see Headers and Exact content


class DlPenguinClient(object):
    def __init__(self, hostName, userName, password, appID):
        self.baseURL, self.appID, self.eServiceEventHandlers = hostName, appID, []
        self.userName, self.password = userName, password
        self._opener = urllib2.build_opener(urllib2.HTTPSHandler(debuglevel=DEBUG_LEVEL), urllib2.HTTPHandler(debuglevel=DEBUG_LEVEL))

    def login(self):
        fh = self._opener.open(self.baseURL + "/penguin/api/authtokens", urllib.urlencode({"userId": self.userName, "password": self.password, "domain": "DL", "appKey": self.appID}))
        loginMessage = json.loads(fh.read())
        self.authToken = loginMessage["content"]["authToken"]
        self.requestToken = loginMessage["content"]["requestToken"]
        self.gateways = loginMessage["content"]["gateways"]

        self.loadDevices()

    def getRelativeURL(self, url, data=None, contentType="application/x-www-form-urlencoded"):
        r = urllib2.Request(re.sub("\\{gatewayGUID}", self.gateways[0]["id"], self.baseURL + url, flags=re.IGNORECASE), headers={'authToken': self.authToken, 'requestToken': self.requestToken, 'appKey': self.appID})
        if data is not None:
            r.data = data
            r.add_header('Content-Type', contentType)
            fh = self._opener.open(r)
        else:
            fh = self._opener.open(r)
        return fh.read()

    def listenToEService(self):
        self.eServiceThread = threading.Thread(target=self.__eServiceHelper)
        self.__eServiceContinue = True
        self.eServiceThread.start()

    def loadDevices(self):
        deviceList = json.loads(self.getRelativeURL("/penguin/api/{gatewayGUID}/devices"))["content"]
        self.devices = dict([(device.id, device) for device in [Device(deviceJSON) for deviceJSON in deviceList]])

    def __getitem__(self, item):
        if self.devices and item in self.devices:
            return self.devices[item]
        return None

    def stopEService(self):
        self.__eServiceContinue = False

    def __eServiceHelper(self):
        fh = self._opener.open(self.baseURL + "/messageRelay/pConnection?uuid=" + str(time.time()) + '&app2="""&key=' + self.gateways[0]["id"], timeout=5)

        longerBuffer = ""
        while self.__eServiceContinue:
            try:
                data = fh.read(1)
                if not data:
                    break
                longerBuffer += data
                if longerBuffer.endswith('"""'):
                    longerBuffer = longerBuffer.strip('\n\r\t *"')
                    if len(longerBuffer) > 0:
                        message = json.loads(longerBuffer)

                        if message["type"] == "device" and message["dev"] in self.devices and message["label"] in self.devices[message["dev"]].attributes:
                            self.devices[message["dev"]].attributes[message["label"]] = message["value"]

                        for eventHandler in self.eServiceEventHandlers:
                            eventHandler(message)
                    longerBuffer = ""
            except SSLError:
                pass  # Caused by read timeout
        print "EService Thread Ending"


class Device(object):
    def __init__(self, deviceJSON):
        self.id = deviceJSON["deviceGuid"]
        self.deviceType = deviceJSON["deviceType"]
        self.attributes = dict([(attribute["label"], attribute["value"]) for attribute in deviceJSON["attributes"]])

    def __getitem__(self, item):
        if self.attributes and item in self.attributes:
            return self.attributes[item]
        return None


class GameView(TemplateView):
    """
    Correct view based on current state of the game.
    """
    def get(self, request, *args, **kwargs):
        try:
            self.game = Game.objects.get(id=kwargs['id'])
        except Game.DoesNotExist:
            raise Http404("Game with given id does not exist")
        self.is_student = kwargs['is_student']

        if self.game.game_state == 1:
            return redirect('board', is_student=self.is_student, id=self.game.id)
        if self.game.game_state == 2:
            return redirect('answer', is_student=self.is_student, game_id=self.game.id, answer_id=self.game.cur_answer_id)
        if self.game.game_state == 3:
            return redirect('select_team', is_student=self.is_student, game_id=self.game.id, team_id=self.game.cur_team_id)

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
        self.is_student = kwargs['is_student']

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
        print self.is_student
        context.update({
            'game': self.game,
            'rows': rows,
            'columns': self.game.columns.all(),
            'is_student': self.is_student,
            # 'logged_in': logged_in,
            # 'user': self.request.user,
            # 'form': form,
            # 'project_reviews': project_reviews,
            # 'own_reviews': own_reviews,
            # 'num_reviews': num_reviews,
            # 'bookmarked': bookmarked
        })


        return context

class ResetView(TemplateView):
    """
    View a specific answer.
    """
    def get(self, request, *args, **kwargs):
        try:
            self.game = Game.objects.get(id=kwargs['id'])
        except Game.DoesNotExist:
            raise Http404("Game with given id does not exist")
        self.is_student = kwargs['is_student']
        if self.is_student == '0': #is teacher

            #set team scores back to zero
            for team in self.game.teams.all():
                team.score = 0
                team.save()
            #set answers back to unanswered
            for answer in self.game.answers.all():
                answer.state = 0
                answer.save()

            self.game.state = 1

        return redirect('game', is_student=self.is_student, id=self.game.id)


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

        self.is_student = kwargs['is_student']

        self.game.game_state = 2
        self.game.cur_answer_id = self.answer.id
        self.game.save()

        return super(AnswerView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AnswerView, self).get_context_data(**kwargs)
        context.update({
            'game': self.game,
            'answer': self.answer,
            'teams': self.game.teams.all(),
            'student': self.is_student,
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
            self.answer = Answer.objects.get(id=self.game.cur_answer_id)
        except Answer.DoesNotExist:
            raise Http404("Answer with given id does not exist")
        try:
            self.team = Team.objects.get(id=kwargs['team_id'])
        except Answer.DoesNotExist:
            raise Http404("Team with given id does not exist")
        self.is_student = kwargs['is_student']
        if self.is_student == '0':
            self.team.score = self.team.score - self.answer.value
            self.team.save()
            self.game.game_state = 2
            self.game.save()

        return redirect('game', is_student=self.is_student, id=self.game.id)

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
            self.answer = Answer.objects.get(id=self.game.cur_answer_id)
        except Answer.DoesNotExist:
            raise Http404("Answer with given id does not exist")
        try:
            self.team = Team.objects.get(id=kwargs['team_id'])
        except Answer.DoesNotExist:
            raise Http404("Team with given id does not exist")
        self.is_student = kwargs['is_student']

        if self.is_student == '0':
            self.team.score = self.team.score + self.answer.value
            self.team.save()

            self.answer.state = 1
            self.answer.save()

            self.game.game_state = 1
            self.game.save()

        return redirect('game', is_student=self.is_student, id=self.game.id)

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
            self.answer = Answer.objects.get(id=self.game.cur_answer_id)
        except Answer.DoesNotExist:
            raise Http404("Answer with given id does not exist")
        try:
            self.team = Team.objects.get(id=kwargs['team_id'])
        except Answer.DoesNotExist:
            raise Http404("Team with given id does not exist")
        self.is_student = kwargs['is_student']

        self.game.game_state = 3
        self.game.cur_team_id = self.team.id
        self.game.save()

        return super(TeamSelectedAnswerView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TeamSelectedAnswerView, self).get_context_data(**kwargs)
        context.update({
            'game': self.game,
            'answer': self.answer,
            'team': self.team,
            'is_student': self.is_student
        })
        return context

