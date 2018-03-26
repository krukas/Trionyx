from trionyx.core.models import BaseModel, models

class Category(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')


class Tag(BaseModel):
    name = models.CharField(max_length=255)


class Post(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()

    publish_date = models.DateTimeField()

    category = models.ForeignKey(Category, related_name='posts')
    tags = models.ManyToManyField(Tag, related_name='posts')
