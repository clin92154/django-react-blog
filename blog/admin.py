from django.contrib import admin
from .models import *

# 註冊User模型
admin.site.register(User)

# 註冊Profile模型
admin.site.register(Profile)

# 註冊Post模型
admin.site.register(Post)

# 註冊Comment模型
admin.site.register(Comment)

admin.site.register(Category)
