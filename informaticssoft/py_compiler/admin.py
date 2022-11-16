from django.contrib import admin

from py_compiler.models import (
    Manual_Section, Manual_Infoblock,
    VideoExample
    )


@admin.register(Manual_Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published')
    list_display_links = ('name',)
    list_editable = ('is_published',)


@admin.register(Manual_Infoblock)
class InfoblockAdmin(admin.ModelAdmin):
    list_display = ('block_name', 'section', 'is_published')
    list_display_links = ('block_name',)
    list_editable = ('is_published',)
    list_filter = ('section__name',)


@admin.register(VideoExample)
class VideoContentAdmin(admin.ModelAdmin):
    list_display = ('get_lesson_name', 'link', 'is_published')
    list_editable = ('is_published',)
    # list_filter = ('get_lesson_name',)

    def get_lesson_name(self, obj):
        return obj.lesson.block_name
    get_lesson_name.short_description = 'тема'
