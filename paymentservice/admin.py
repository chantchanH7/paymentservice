from django.contrib import admin

# paymentservice your models here.
from paymentservice.models import *

# paymentservice your models here.
admin.site.register(User)
admin.site.register(RefundOrder)
admin.site.register(Order)