from django.db import models


class EMRServer(models.Model):
    server_address = models.CharField(max_length=255)
    api_endpoint = models.CharField(max_length=255)
    credentials = models.CharField(max_length=255)
    last_claim_id = models.IntegerField(default=0)

    def __str__(self):
        return self.server_address
