from trionyx import models
from django.utils import timezone

class Category(models.BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    class Meta:
        verbose_name_plural = 'Categories'


class Tag(models.BaseModel):
    name = models.CharField(max_length=255)


class Post(models.BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()

    publish_date = models.DateTimeField()
    sale_date = models.DateField(default=timezone.now)

    category = models.ForeignKey(Category, models.CASCADE, related_name='posts')
    tags = models.ManyToManyField(Tag, related_name='posts')

    STATUS_NEW = 1
    STATUS_DRAFT = 2
    STATUS_PUBLISHED = 3

    STATUS_CHOISES = [
        (STATUS_NEW, 'New'),
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    status = models.IntegerField(choices=STATUS_CHOISES, default=STATUS_NEW)

    price = models.PriceField(default=0.0)
