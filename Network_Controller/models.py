# https://docs.djangoproject.com/en/4.2/topics/db/models/

from django.db import models


class Food(models.Model):
    lvl = models.IntegerField()
    time = models.DateTimeField()
    containerID = models.CharField(max_length=100)


class FoodConfig(models.Model):
    containerID = models.CharField(max_length=100)
    lvlMax = models.IntegerField(default=1000)
    lvlThresholdStart = models.IntegerField(default=300)
    lvlThresholdStop = models.IntegerField(default=700)
    lvlMin = models.IntegerField(0)
    defaultMax = 1000
    defaultMin = 0
    defaultThresholdStart = 300
    defaultThresholdStop = 700


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
    defaultHigh = 200
    defaultLow = 40


class Hatch(models.Model):
    nothing = 0
    inside = 1
    outside = 2
    time = models.DateTimeField()
    hatchId = models.CharField(max_length=100)
    DIRECTION_TRIGGER_CHOICES = (
        (0, 'Nothing'),
        (1, 'Inside'),
        (2, 'Outside')
    )
    direction_Trigger = models.CharField(max_length=10,
                                         choices=DIRECTION_TRIGGER_CHOICES,
                                         default=0
                                         )


class HatchConfig(models.Model):
    hatchId = models.CharField(max_length=100)
    allowOpen = models.BooleanField(default=False)
    defaultAllow = False


class LiveClient(models.Model):
    nodeId = models.IntegerField()
    nodeCoapName = models.CharField(max_length=16, default="")
    nodeCoapAddress = models.CharField(max_length=30, default="")
    unknown = 0
    food = 1
    heartbeat = 2
    hatch = 3
    NODE_TYPES = (
        (unknown, 'unknown'),
        (food, 'food'),
        (heartbeat, 'heartbeat'),
        (hatch, 'hatch')
    )
    isFree = models.BooleanField(default=True)
    nodeType = models.CharField(max_length=10,
                                choices=NODE_TYPES,
                                default=unknown
                                )
    isActuator = models.BooleanField(default=False)
    lastInteraction = models.DateTimeField()


class Pair(models.Model):
    nodeIdMQTT = models.IntegerField()
    nodeIdCOAP = models.IntegerField()
