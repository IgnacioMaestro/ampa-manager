from django.db import models


class CustodyImportationActionGroup(models.Model):
    row = models.ForeignKey('CustodyImportationRow', on_delete=models.CASCADE)
    child_action = models.ForeignKey('CustodyImportationActionChild', on_delete=models.CASCADE)
