from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify
import os
from django.contrib.auth.hashers import make_password

class User(AbstractUser):
    username = first_name = last_name = None
    id = models.CharField(max_length=255)
    email = models.EmailField(_("email address"),primary_key=True,unique=True)
    password = models.CharField(max_length=255)
    createtime = models.DateTimeField(auto_now_add=True,auto_now=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ()

    objects = UserManager()

    def __str__(self) :
        return self.id

    def save(self, *args, **kwargs):
        self.id = self.email.split("@")[0]
        super().save(*args, **kwargs)




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uid = models.CharField(max_length=20,blank=True,primary_key=True)
    name = models.CharField(max_length=20,blank=True)
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.uid
    
    def save(self, *args, **kwargs):
        self.uid = str(self.user.id)
        super().save(*args, **kwargs)
    @property
    def filename(self):
        return os.path.basename(self.image.name)

class Category(models.Model):
    name = models.CharField(_("Category name"), max_length=100)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

def get_image_filename(instance, filename):
    name = instance.product.name
    slug = slugify(name)
    return f"products/{slug}-{filename}"




class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    categories = models.ManyToManyField(Category, related_name="posts_list", blank=True)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comments = models.IntegerField(default=0)
    class Meta:
        ordering = ("-created_at",)

        
    def __str__(self):
        return self.title
    


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f'{self.author.id} - {self.post.title}'


    def save(self, *args, **kwargs):
        self.post.comments = len(Comment.objects.filter(post=self.post.id))
        self.post.save()
        print(self.post.comments)
        super().save(*args, **kwargs)