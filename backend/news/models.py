from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.template.defaultfilters import slugify

class Categories(models.TextChoices):
    GENERAL = "general"
    POLITICS = 'politics'
    STYLE = 'style'
    SCIENCE = 'science'
    TECHNOLOGY = 'technology'
    CULTURE = 'culture'
    BUSINESS = 'business'
    FASHION = 'fashion'
    Environment = 'environment'
    TRAVEL = 'travel'
    HEALTH = 'health'

class NewsPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    category = models.CharField(max_length=50, choices=Categories, default=Categories.GENERAL)
    tags = models.CharField(max_length=2000, blank=True, null=True)
    picture = models.ImageField(upload_to='photos/%Y/%m/%d')
    excerpt = models.CharField(max_length=200)
    month = models.CharField(max_length=3)
    day = models.CharField(max_length=2)
    content = models.TextField()
    featured = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_created = models.DateTimeField(default=datetime.now, blank=True)

    def save(self, *args, **kwargs):
        original_slug = slugify(self.title)
        queryset = NewsPost.objects.all().filter(slug__iexact=original_slug).count()

        count = 1
        slug = original_slug
        while(queryset):
            slug = original_slug + '-' + str(count)
            count += 1
            queryset = NewsPost.objects.all().filter(slug__iexact=slug).count()

        self.slug = slug

        if self.featured:
            try:
                temp = NewsPost.objects.get(featured=True)
                if self != temp:
                    temp.featured = False
                    temp.save()
            except NewsPost.DoesNotExist:
                pass
        
        super(NewsPost, self).save(*args, **kwargs)

    def __str__(self):
        return self.title





class View(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    news = models.ForeignKey(NewsPost, on_delete=models.CASCADE, related_name='views')
    ip_address = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'news', 'ip_address')  # Prevent duplicate views

    def _str_(self):
        return f"View by {self.user or 'Anonymous'} on {self.news.title}"
    
    

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.ForeignKey(NewsPost, on_delete=models.CASCADE, related_name='likes')
    liked = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'news')

    def _str_(self):
        return f"{self.user.username} {'liked' if self.liked else 'disliked'} {self.news.title}"
