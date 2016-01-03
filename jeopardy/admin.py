from django.contrib import admin

from jeopardy.models import Game, Team, Column, Answer


class GameAdmin(admin.ModelAdmin):
    pass

admin.site.register(Game, GameAdmin)


class TeamAdmin(admin.ModelAdmin):
    pass


admin.site.register(Team, TeamAdmin)


class ColumnAdmin(admin.ModelAdmin):
    pass


admin.site.register(Column, ColumnAdmin)

class AnswerAdmin(admin.ModelAdmin):
    pass


admin.site.register(Answer, AnswerAdmin)
