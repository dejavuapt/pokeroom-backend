from django.db import models

class Strategies(models.TextChoices):
    POKER = ('P', 'PokerPlanning')
    # RETRO = ('R', 'Retrospective') # IN FUTURE
    
class RoomStatuses(models.TextChoices):
    OPEN = ('O', 'Opened')
    START = ('S', 'Started')
    FINISH = ('F', 'Finished')
    CLOSE = ('C', 'Closed')
    
class RoomMembersRole(models.TextChoices):
    HOST = ('H', 'Host')
    MEMBER = ('M', 'Member')
    GUEST = ('G', 'Guest')