from django.db import models


class Manual_Section(models.Model):
    name = models.CharField('название', max_length=200, unique=True)
    is_published = models.BooleanField('опубликовано', default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'раздел'
        verbose_name_plural = 'разделы'


class Manual_Infoblock(models.Model):
    section = models.ForeignKey(
        Manual_Section,
        verbose_name='раздел',
        on_delete=models.CASCADE,
        related_name='infoblock'
    )
    block_name = models.CharField('название', max_length=150, unique=True)
    text = models.TextField('материал по теме')
    is_published = models.BooleanField('опубликовано', default=True)

    class Meta:
        verbose_name = 'статья'
        verbose_name_plural = 'статьи'
