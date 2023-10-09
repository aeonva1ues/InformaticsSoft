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

    def __str__(self):
        return f'{self.block_name} из раздела {self.section}'

    class Meta:
        verbose_name = 'статья'
        verbose_name_plural = 'статьи'


class VideoManager(models.Manager):
    def published(self):
        return (
            self.get_queryset()
            .select_related('lesson')
            .filter(is_published=True, lesson__is_published=True)
        )


class VideoExample(models.Model):
    lesson = models.ForeignKey(
        Manual_Infoblock,
        verbose_name='тема',
        on_delete=models.CASCADE,
        related_name='videoexample'
    )
    link = models.URLField(
        'ссылка на видео',
        max_length=150
    )
    is_published = models.BooleanField('отображать', default=True)

    def __str__(self):
        return self.link

    class Meta:
        verbose_name = 'видеоролик'
        verbose_name_plural = 'видеоролики'

    objects = VideoManager()
