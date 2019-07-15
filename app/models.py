from django.db import models


class GoogleQuery(models.model):
    text = models.TextField()
    
