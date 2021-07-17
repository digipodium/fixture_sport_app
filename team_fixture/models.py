from django.db import models

# Create your models here.
from django.db import models
import datetime
from django.core.validators import MinValueValidator
# Create your models here.


class TeamFixture(models.Model):
    pub_date = models.DateTimeField('date published', null=True)
    icon = models.ImageField(upload_to='icons',verbose_name='image',)
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True, default='', null=True)
    rounds = models.IntegerField(default=0)
    start_date = models.DateField('Start date')
    matches_per_day = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    current_round = models.IntegerField(default=0)

    @property
    def icon_url(self):
        if self.icon:
            return self.icon.url
        return '/static/img/icons/fixture.png'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        pub_date = datetime.datetime.utcnow()
        super(TeamFixture, self).save(*args, **kwargs)


class Team(models.Model):
    class Meta:
        unique_together = (('rank', 'fixture'))
    rank = models.IntegerField()
    fixture = models.ForeignKey(TeamFixture, related_name="teams",on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class TeamPlayer(models.Model):
    name = models.CharField(max_length=100)
    number = models.IntegerField()
    team = models.ForeignKey(Team, related_name="teamplayers",on_delete=models.CASCADE)
    def __str__(self):
        return self.name


class TeamMatch(models.Model):
    class Meta:
        verbose_name_plural = "Team Matches"

    @property
    def description(self):
        return repr(self)

    @property
    def name(self):
        if self.match_number:
            return "{} - Match {}".format(self.fixture.name, self.match_number)
        else:
            return "{}".format(self.fixture.name)

    MATCH_STATUS = [
        ("BYE", 'BYE'),
        ("Not Scheduled", 'Not Scheduled'),
        ("Scheduled", "Scheduled"),
        ('Finished', 'Finished')
    ]
    date = models.DateField('Match Date', null=True, blank=True)
    match_number = models.IntegerField(blank=True, null=True)
    fixture = models.ForeignKey(TeamFixture, related_name="matches", on_delete=models.DO_NOTHING)
    match_round = models.IntegerField()
    left_previous = models.OneToOneField('self', blank=True, null=True, related_name="left_next_match",on_delete=models.DO_NOTHING)
    right_previous = models.OneToOneField('self', blank=True, null=True, related_name="right_next_match",on_delete=models.DO_NOTHING)

    team_1 = models.ForeignKey(Team, blank=True, null=True, related_name="left_matches",on_delete=models.DO_NOTHING)
    team_2 = models.ForeignKey(Team, blank=True, null=True, related_name="right_matches",on_delete=models.DO_NOTHING)

    status = models.CharField(max_length=20, choices=MATCH_STATUS, default='Not Scheduled')

    team_1_score = models.PositiveIntegerField(null=True, blank=True)
    team_2_score = models.PositiveIntegerField(null=True, blank=True)

    winner = models.ForeignKey(Team, blank=True, null=True, related_name="matches_won",on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{}: {}".format(self.name, self.description)

    def __repr__(self):
        if self.status == 'Finished':
            return "{} {}-{} {}".format(self.team_1, self.team_1_score, self.team_2_score, self.team_2)

        _right = "BYE"
        _left = "BYE"
        if self.team_1:
            _left = "{}".format(self.team_1)
        elif self.left_previous:
            _left = "Winners (Match {})".format(self.left_previous.match_number)

        if self.team_2:
            _right = "{}".format(self.team_2)
        elif self.right_previous:
            _right = "Winners (Match {})".format(self.right_previous.match_number)

        if _right == "BYE" and _left == "BYE":
            _right = "TBD"
            _left = "TBD"

        return "{} vs {}".format(_left, _right)

    def save(self, *args, **kwargs):
        self.status = "Not Scheduled"
        self.winner = None

        if self.team_1 and self.team_2:
            self.status = 'Scheduled'
            self.team_1_score = self.team_1_score or 0
            self.team_2_score = self.team_2_score or 0

            if self.team_1_score == self.team_2_score:
                self.team_1_score = None
                self.team_2_score = None
                self.winner=None
            elif self.team_1_score > self.team_2_score:
                self.winner = self.team_1
                self.status = "Finished"
            else:
                self.winner = self.team_2
                self.status = "Finished"


        elif self.team_1 or self.team_2:
            self.team_1_score = None
            self.team_2_score = None
            if not (self.team_1 or self.left_previous):
                self.status = 'BYE'
                self.winner = self.team_2
            elif not (self.team_2 or self.right_previous):
                self.status = 'BYE'
                self.winner = self.team_1

        super(TeamMatch, self).save(*args, **kwargs)

        if self.winner:
            try:
                _next_left = self.left_next_match
                if _next_left:
                    _next_left.team_1 = self.winner
                    _next_left.save()
            except:
                pass
            try:
                _next_right = self.right_next_match
                if _next_right:
                    _next_right.team_2 = self.winner
                    _next_right.save()
            except:
                pass

        if self.status=="Finished":
            self.fixture.current_round = max(self.fixture.current_round, self.match_round)
            self.fixture.save()

    def is_bye(self):
        return self.status == 'BYE', self.team_1 or self.team_2

    def get_player_names(self):
        return [str(self.team_1) if self.team_1 else None, str(self.team_2) if self.team_2 else None,]

    def get_result_values(self):
        return [self.team_1_score, self.team_2_score,]