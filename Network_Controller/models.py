# https://docs.djangoproject.com/en/4.2/topics/db/models/

from django.db import models


class Food(models.Model):
    lvl = models.IntegerField()
    time = models.DateTimeField()
    containerID = models.CharField(max_length=100)


class FoodConfig(models.Model):
    containerID = models.CharField(max_length=100)
    lvlMax = models.IntegerField(default=1000)
    lvlThreshold = models.IntegerField(default=300)
    lvlMin = models.IntegerField(0)


class Heartbeat(models.Model):
    frequency = models.IntegerField()
    time = models.DateTimeField()
    petID = models.CharField(max_length=100)


class HeartBeatConfig(models.Model):
    petID = models.CharField(max_length=100)
    max = 300
    high_Threshold = models.IntegerField(default=200)
    low_Threshold = models.IntegerField(default=40)
    min = 0


class Trapdoor(models.Model):
    IN = 'INSIDE'
    OUT = 'OUTSIDE'
    DEF = 'DEFAULT'
    time = models.DateTimeField()
    trapdoorId = models.CharField(max_length=100)
    DIRECTION_TRIGGER_CHOICES = (
        (IN, 'Inside'),
        (OUT, 'Outside'),
        (DEF, 'Default')
    )
    direction_Trigger = models.CharField(max_length=10,
                                         choices=DIRECTION_TRIGGER_CHOICES,
                                         default=DEF
                                         )


class TrapdoorConfig(models.Model):
    trapdoorId = models.CharField(max_length=100)
    allowOpen = models.BooleanField(default=False)
