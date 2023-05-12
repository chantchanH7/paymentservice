from django.db import models


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    password = models.CharField(max_length=200)
    # 账户余额
    balance = models.IntegerField(null=True)
    last_login = models.DateTimeField(auto_now=True)


class Order(models.Model):
    from_account = models.IntegerField(null=True)
    merchant_order_id = models.IntegerField()
    order_time = models.DateTimeField()
    payment_time = models.DateTimeField(null=True)
    price = models.IntegerField(null=True)
    stamp = models.CharField(max_length=255)
    to_account = models.IntegerField()


class RefundOrder(models.Model):
    refund_time = models.CharField(max_length=255)
    payment_id = models.IntegerField()
    price = models.IntegerField()