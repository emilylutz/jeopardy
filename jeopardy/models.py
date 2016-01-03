from django.db import models

class Game(models.Model):
    """
    The jeopardy game state.
    """
    GAME_STATES = (
        (0, 'Game Initialization'),
        (1, 'Board View'),
        (2, 'Presenting Answer Pending Person'),
        (3, 'Validating Question'),
        (4, 'Team Scores'),
    )

    name = models.CharField(max_length=128)
    game_state = models.IntegerField(choices=GAME_STATES)

    class Meta:
        verbose_name = 'jeopardy game'
        verbose_name_plural = 'jeopardy games'

    def __unicode__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=128)
    score = models.IntegerField()
    # color = models.ColorField()
    game = models.ForeignKey(Game, related_name="teams")

    class Meta:
        verbose_name = 'team'
        verbose_name_plural = 'teams'

    def __unicode__(self):
        return self.game.name + " - " + self.name

class Column(models.Model):
    name = models.CharField(max_length=128)
    game = models.ForeignKey(Game, related_name="columns")

    class Meta:
        verbose_name = 'column'
        verbose_name_plural = 'columns'

    def __unicode__(self):
        return self.game.name + " - " + self.name

class Answer(models.Model):
    ANSWER_STATES = (
        (0, 'Not Answered'),
        (1, 'Answered'),
    )

    answer = models.CharField(max_length=128)
    question = models.CharField(max_length=128)
    value = models.IntegerField()
    row = models.IntegerField()
    column = models.ForeignKey(Column, related_name="answers")
    game = models.ForeignKey(Game, related_name="answers")
    state = models.IntegerField(choices=ANSWER_STATES, default=0)

    class Meta:
        verbose_name = 'answer'
        verbose_name_plural = 'answers'

    def __unicode__(self):
        return self.game.name + " - " + self.answer