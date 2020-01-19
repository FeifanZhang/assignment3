from django.db import models
from loginApp.models import *

# Create your models here.
class Tuple(models.Model):
    #on_delete: 联级删除，即主表中数据删除后，附表中的数据也会删除
    #fields.E300: 跨模块的表 外键之前要加上表的名称
    user=models.ForeignKey('loginApp.User',on_delete=models.CASCADE)
    subject=models.CharField(max_length=128)
    predicate=models.CharField(max_length=128)
    obj=models.CharField(max_length=128)
    def __str__(self):
        return str(self.user_id)+self.subject+self.predicate+self.obj