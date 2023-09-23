# https://docs.djangoproject.com/en/4.2/topics/db/models/

from django.db import models


class Food(models.Model):
    lvl = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)
    containerID = models.CharField(max_length=100)

    @classmethod
    def preprocess_grafana(cls, query_set):
        result = []
        for item in query_set:
            result.append(item)
        return result


class FoodConfig(models.Model):
    containerID = models.CharField(max_length=100)
    lvlMax = models.IntegerField(default=1000)
    lvlThresholdStart = models.IntegerField(default=300)
    lvlThresholdStop = models.IntegerField(default=700)
    lvlMin = models.IntegerField(default=0)
    defaultMax = 1000
    defaultMin = 0
    defaultThresholdStart = 300
    defaultThresholdStop = 700


class Heartbeat(models.Model):
    frequency = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)
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
    time = models.DateTimeField(auto_now_add=True)
    hatchId = models.CharField(max_length=100)
    DIRECTION_TRIGGER_CHOICES = [
        ('Nothing', 'Nothing'),
        ('Inside', 'Inside'),
        ('Outside', 'Outside'),
    ]

    direction_Trigger = models.CharField(max_length=10,
                                         choices=DIRECTION_TRIGGER_CHOICES,
                                         default='Nothing'
                                         )


class HatchConfig(models.Model):
    hatchId = models.CharField(max_length=100)
    allowOpen = models.BooleanField(default=False)
    defaultAllow = True


class LiveClient(models.Model):
    nodeId = models.IntegerField()
    nodeCoapAddress = models.CharField(max_length=30, default="", blank=True)

    NODE_TYPES = [
        ('unknown', 'unknown'),
        ('food', 'food'),
        ('heartbeat', 'heartbeat'),
        ('hatch', 'hatch')
    ]
    isFree = models.BooleanField(default=True)
    nodeType = models.CharField(max_length=10,
                                choices=NODE_TYPES,
                                default='unknown'
                                )
    isActuator = models.BooleanField(default=False)
    lastInteraction = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        protocol = "  MQTT"
        if self.isActuator:
            protocol = "  CoAP"
        return "LiveClient "+str(self.nodeId)+" type:"+self.nodeType+protocol


class Pair(models.Model):
    nodeIdMQTT = models.IntegerField()
    nodeIdCOAP = models.IntegerField()
