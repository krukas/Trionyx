from trionyx.trionyx.models import BaseModel, models

class Category(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    class Meta:
        verbose_name_plural = 'Categories'


class Tag(BaseModel):
    name = models.CharField(max_length=255)


class Post(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()

    publish_date = models.DateTimeField()

    category = models.ForeignKey(Category, related_name='posts')
    tags = models.ManyToManyField(Tag, related_name='posts')
