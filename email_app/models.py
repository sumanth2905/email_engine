from django.db import models
from django.contrib.auth.models import User
from elasticsearch_dsl import Document, Date, Text, Keyword
from datetime import datetime

class EmailAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class EmailMessage(Document):
    subject = Text()
    sender = Keyword()
    recipient = Keyword()
    message_body = Text()
    timestamp = Date()

    class Index:
        name = 'emails'

    def save(self, **kwargs):
        self.timestamp = datetime.now()
        return super().save(**kwargs)

