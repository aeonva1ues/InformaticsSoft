import os
from datetime import datetime
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from .forms import UploadFileForm
from .models import Section, FileInStorage


# Performancetech - софт для удобного длительного хранения файлов и данных для выступлений.
# Доступ к странице имеют только суперпользователи. Суперпользователь может смотреть, скачивать и загружать файлы.

def performancetech_main_view(request):
    base_dir = settings.BASE_DIR
    static_dir = f'{base_dir}/static'
    static_url = '../static'

    oneColor_files = os.listdir(f'{static_dir}/images/oneColor')
    oneColor_images = []
    image_id = 0
    for oneColor_file in oneColor_files:
        string_filename = str(oneColor_file)
        if string_filename.endswith('.png') or string_filename.endswith('.jpeg') or string_filename.endswith('.jpg') \
            or string_filename.endswith('.gif'):
            oneColor_images.append(
                {
                    'image_id': image_id,
                    'path': f'{static_url}/images/oneColor/{string_filename}',
                    'name': string_filename,
                }
            )
            image_id+=1

    loaded_dirs = os.listdir(f'{static_dir}/images/loaded')
    loaded_sections = []
    for loaded_dir in loaded_dirs:
        if '.' not in loaded_dir:
            dir_files = os.listdir(f'{static_dir}/images/loaded/{loaded_dir}')
            loaded_images = []
            section_from_db = Section.objects.get(section_name=str(loaded_dir))
            if section_from_db:
                files_found = False
                files_from_section_in_db = FileInStorage.objects.filter(file_type='images', section=section_from_db)
                if files_from_section_in_db:
                    files_found = True
            for dir_file in dir_files:
                string_filename = str(dir_file)
                load_date = None
                load_time = None
                if files_found:
                    for db_note in files_from_section_in_db:
                        if db_note.file_name == string_filename:
                            load_date = db_note.load_date
                            load_time = db_note.load_time
                            image_id = db_note.id
                            break
                if string_filename.endswith('.png') or string_filename.endswith('.jpeg') \
                        or string_filename.endswith('.jpg') or string_filename.endswith('.gif'):
                    loaded_images.append(
                        {
                            'image_id': image_id,
                            'path': f'{static_url}/images/loaded/{loaded_dir}/{string_filename}',
                            'name': string_filename,
                            'load_date': load_date,
                            'load_time': load_time
                        }
                    )

            loaded_sections.append({
                'name': str(loaded_dir),
                'files_count': str(len(dir_files)),
                'images': loaded_images
                }
            )
    loaded_audio_dir = os.listdir(f'{static_dir}/audio/loaded')
    loaded_audio_sections = []
    for dir in loaded_audio_dir:
        if '.' not in dir:
            dir_files = os.listdir(f'{static_dir}/audio/loaded/{dir}')
            loaded_audio = []
            section_from_db = Section.objects.get(section_name=str(dir))
            if section_from_db:
                files_found = False
                files_from_section_in_db = FileInStorage.objects.filter(file_type='audio', section=section_from_db)
                if files_from_section_in_db:
                    files_found = True
            for dir_file in dir_files:
                string_filename = str(dir_file)
                load_date = None
                load_time = None
                if files_found:
                    for db_note in files_from_section_in_db:
                        if db_note.file_name == string_filename:
                            load_date = db_note.load_date
                            load_time = db_note.load_time
                            audio_id = db_note.id
                            break
                if string_filename.endswith('.mp3') or string_filename.endswith('.m4a') \
                        or string_filename.endswith('.ogg') or string_filename.endswith('.wav'):
                    loaded_audio.append(
                        {
                            'audio_id': audio_id,
                            'path': f'{static_url}/audio/loaded/{dir}/{string_filename}',
                            'name': string_filename,
                            'load_date': load_date,
                            'load_time': load_time
                        }
                    )
                
            loaded_audio_sections.append({
                'name': str(dir),
                'files_count': str(len(dir_files)),
                'audio': loaded_audio  
                }
            )
    context = {
        'oneColor_images': oneColor_images,
        'loaded_sections': loaded_sections,  # Разделы загруженных фотографий
        'loaded_audio_sections': loaded_audio_sections,
        'active': 'mainmenu'
    }
    return render(request, 'performancetech/mainpage.html', context)


def performancetech_load_view(request):
    sections = []
    dirs = os.listdir(f'{settings.BASE_DIR}/static/images/loaded')
    for dir in dirs:
        if '.' not in dir:
            sections.append(dir)
    context = {
        'active': 'loadpage',
        'sections': sections
    }
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        context['with_error'] = 'None'
        if form.is_valid():
            filename = str(request.FILES['fileName']).strip()
            section_name = str(request.POST['sectionName']).strip()
            correct_type = False
            if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg') \
                or filename.endswith('.gif'):
                file_type = 'images'
                correct_type = True
            elif filename.endswith('.mp3') or filename.endswith('.m4a') or filename.endswith('.ogg') \
                or filename.endswith('.wav'):
                file_type = 'audio'
                correct_type = True
            if correct_type:
                all_dirs = os.listdir(f'{settings.BASE_DIR}/static/{file_type}/loaded')
                path_to_all_dirs = f'{settings.BASE_DIR}/static/{file_type}/loaded'
                dir_exists = False
                dir_to_load = f'{path_to_all_dirs}/{section_name}'

                for dir in all_dirs:
                    if dir == section_name:
                        dir_exists = True
                        break
                section_in_db, was_created = Section.objects.get_or_create(section_name=section_name)
                if not dir_exists:
                    os.makedirs(dir_to_load)
                files_from_dir = os.listdir(dir_to_load)
                no_file_in_dir = True
                for file in files_from_dir:
                    if file.strip() == filename:
                        context['with_error'] = 'Файл с таким именем уже существует'
                        no_file_in_dir = False
                if no_file_in_dir:
                    with open(f'{path_to_all_dirs}/{section_name}/{filename}', 'wb+') as destination:
                        for chunk in request.FILES['fileName'].chunks():
                            destination.write(chunk)
                    new_file = FileInStorage(
                        file_name = filename,
                        file_type = file_type,
                        path = f'{path_to_all_dirs}/{section_name}/{filename}',
                        load_date = str(datetime.now()).split()[0],
                        load_time = str(datetime.now()).split()[1].split('.')[0],
                        section = section_in_db
                    )
                    new_file.save()
            else:
                context['with_error'] = 'Файлы данного расширения недоступны для загрузки'
        else:
            context['with_error'] = 'Обязательный пункт(ы) пропущен'
            
    return render(request, 'performancetech/loadpage.html', context)


def getFileInfoPost(request):
        file_id = request.POST.get('id')
        file_from_db = FileInStorage.objects.get(id=file_id)
        file_info = {
            'path': file_from_db.path,
            'name': file_from_db.file_name,
            'load_date': file_from_db.load_date,
            'load_time': file_from_db.load_time
        }

        return JsonResponse(file_info,status=200)


def deleteFilePost(request):
    file_id = request.POST.get('id')
    file_path = request.POST.get('path')
    file_in_db = FileInStorage.objects.get(id=file_id)
    file_in_db.delete()  # удаление записи файла из бд
    os.remove(file_path)
    print(f'Файл({file_id}) удален: {file_path}')
    return JsonResponse({'status': 'done'}, status=200)