from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)

# 모델 mysql 속성값들 설정
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, nickname, u_id, telephone, password=None):
        if not email:
            raise ValueError('Users must have an email')
        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname,
            u_id=u_id,
            telephone=telephone
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, u_id, telephone, password):
        user = self.create_user(
            email=self.normalize_email(email),
            nickname=nickname,
            password=password,
            u_id=u_id,
            telephone=telephone
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    nickname = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=50, unique=True)
    u_id = models.CharField(max_length=15, unique=True)
    telephone = models.CharField(max_length=11)
    profile_pic = models.ImageField(null=True, blank=True)

    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'u_id'
    REQUIRED_FIELDS = ['email', 'nickname', 'telephone']

    def __str__(self):
        return self.email


class BaseDictionary(models.Model):
    name = models.CharField(max_length=300)
    mean = models.CharField(max_length=500)
    example = models.CharField(max_length=500)

    class Meta:
        abstract = True


class BaseRPC(models.Model):
    content = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SDictionary(BaseDictionary):
    replace = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class KDictionary(BaseDictionary):

    def __str__(self):
        return self.name


class Request(BaseRPC):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_request')
    title = models.CharField(max_length=25)
    name = models.CharField(max_length=16)

    def __str__(self):
        return self.title


class Post(BaseRPC):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_post')
    title = models.CharField(max_length=25)

    def __str__(self):
        return self.title


class Comment(BaseRPC):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comment')
    color = models.CharField(max_length=7, default='#000000', blank=True)

    def __str__(self):
        return self.content


class Vote(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='request_vote')
    tag = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.request)


class Analyzer(models.Model):
    input = models.CharField(max_length=500)
    output = models.CharField(max_length=500)
    word = models.CharField(max_length=300)

    def __str__(self):
        return self.word