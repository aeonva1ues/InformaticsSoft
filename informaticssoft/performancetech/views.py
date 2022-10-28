import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .forms import CreateNote, CreateWebPresentation, LoginUser, UploadFileForm
from .models import (DeletedFile, FileInStorage, LoadedFile, Section, UserNote,
                     WebPresentation)

'''
Performancetech -
        софт для удобного длительного хранения файлов и данных для выступлений.
Доступ к странице имеют только суперпользователи.
Суперпользователь может смотреть, скачивать и загружать файлы.
'''


def login_view(request):
    context = {}
    if request.method == 'POST':
        form = LoginUser(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('/performancetech/')
            else:
                context['error'] = 'Неверно указаны данные'
        else:
            context['error'] = 'Обязательное поле пропущено'
    return render(request, 'login.html', context=context)


@login_required
def logout_view(request):
    logout(request)
    return redirect('/login/')


@login_required
def performancetech_main_view(request):
    base_dir = settings.BASE_DIR
    static_dir = f'{base_dir}/media'
    static_url = '../media'

    oneColor_files = os.listdir(f'{static_dir}/images/oneColor')
    oneColor_images = []
    image_id = 1
    for oneColor_file in oneColor_files:
        string_filename = str(oneColor_file)
        if string_filename.endswith('.png') \
                or string_filename.endswith('.jpeg') \
                or string_filename.endswith('.jpg') \
                or string_filename.endswith('.gif'):
            oneColor_images.append(
                {
                    'image_id': image_id,
                    'path': f'{static_url}/images/oneColor/{string_filename}',
                    'name': string_filename,
                }
            )
            image_id += 1

    loaded_dirs = os.listdir(f'{static_dir}/images/loaded')
    loaded_sections = []
    for loaded_dir in loaded_dirs:
        if '.' not in loaded_dir:
            dir_files = os.listdir(f'{static_dir}/images/loaded/{loaded_dir}')
            loaded_images = []
            section_from_db = Section.objects.get(section_name=str(loaded_dir))
            if section_from_db:
                files_found = False
                files_from_section_in_db = FileInStorage.objects.filter(
                    file_type='images',
                    section=section_from_db
                    )
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
                if string_filename.endswith('.png') \
                        or string_filename.endswith('.jpeg') \
                        or string_filename.endswith('.jpg') \
                        or string_filename.endswith('.gif'):
                    loaded_images.append(
                        {
                            'image_id': image_id,
                            'path': (
                                f'{static_url}/images/loaded/'
                                f'{loaded_dir}/{string_filename}'
                            ),
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
                files_from_section_in_db = FileInStorage.objects.filter(
                    file_type='audio',
                    section=section_from_db
                    )
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
                if string_filename.endswith('.mp3') \
                        or string_filename.endswith('.m4a') \
                        or string_filename.endswith('.ogg') \
                        or string_filename.endswith('.wav'):
                    loaded_audio.append(
                        {
                            'audio_id': audio_id,
                            'path': (
                                f'{static_url}/audio/loaded/'
                                f'{dir}/{string_filename}'
                                ),
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


@login_required
def performancetech_load_view(request):
    sections = []
    dirs = os.listdir(f'{settings.BASE_DIR}/media/images/loaded')
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
            form_files = request.FILES.getlist('fileName')
            section_name = str(request.POST['sectionName']).strip()
            if section_name != 'default':
                for form_file in form_files:
                    # filename = str(request.FILES['fileName']).strip()
                    filename = str(form_file).strip()
                    correct_type = False
                    if filename.endswith('.png') \
                            or filename.endswith('.jpg') \
                            or filename.endswith('.jpeg') \
                            or filename.endswith('.gif'):
                        file_type = 'images'
                        correct_type = True
                    elif filename.endswith('.mp3') \
                            or filename.endswith('.m4a') \
                            or filename.endswith('.ogg') \
                            or filename.endswith('.wav'):
                        file_type = 'audio'
                        correct_type = True
                    if correct_type:
                        all_dirs = os.listdir(
                            f'{settings.BASE_DIR}/media/{file_type}/loaded'
                            )
                        path_to_all_dirs = (
                            f'{settings.BASE_DIR}/media/'
                            f'{file_type}/loaded'
                            )
                        dir_exists = False
                        dir_to_load = f'{path_to_all_dirs}/{section_name}'

                        for dir in all_dirs:
                            if dir == section_name:
                                dir_exists = True
                                break
                        section_in_db, was_created = Section.objects\
                            .get_or_create(section_name=section_name)
                        if not dir_exists:
                            os.makedirs(dir_to_load)
                        files_from_dir = os.listdir(dir_to_load)
                        no_file_in_dir = True
                        for file_from_dir in files_from_dir:
                            if file_from_dir.strip() == filename:
                                context['with_error'] = (
                                    'Файл с таким именем '
                                    f'уже существует ({filename})'
                                    )
                                no_file_in_dir = False
                        if no_file_in_dir:
                            with open(
                                (
                                    f'{path_to_all_dirs}'
                                    f'/{section_name}/{filename}'
                                ),
                                    'wb+') as destination:
                                for chunk in form_file.chunks():
                                    destination.write(chunk)
                            new_file = FileInStorage(
                                file_name=filename,
                                file_type=file_type,
                                path=(
                                        f'{path_to_all_dirs}'
                                        f'/{section_name}/{filename}'
                                    ),
                                load_date=str(datetime.now()).split()[0],
                                load_time=str(datetime.now())
                                .split()[1].split('.')[0],
                                section=section_in_db
                            )
                            new_file.save()
                            new_loaded_file = LoadedFile(
                                file_name=filename,
                                file_type=file_type,
                                section_name=section_in_db.section_name,
                                load_date=str(datetime.now()).split()[0],
                                load_time=str(datetime.now())
                                .split()[1].split('.')[0]
                            )
                            new_loaded_file.save()
                    else:
                        context['with_error'] = (
                            'Файлы данного расширения недоступны '
                            f'для загрузки (.{filename.split(".")[1]})'
                            )
            else:
                context['with_error'] = 'Недопустимое название раздела'
        else:
            context['with_error'] = 'Обязательный пункт(ы) пропущен'
    return render(request, 'performancetech/loadpage.html', context)


@login_required
def getFileInfoPost(request):
    file_id = request.POST.get('id')
    file_from_db = FileInStorage.objects.get(id=file_id)
    file_info = {
        'path': file_from_db.path,
        'name': file_from_db.file_name,
        'load_date': file_from_db.load_date,
        'load_time': file_from_db.load_time
    }

    return JsonResponse(file_info, status=200)


@login_required
def deleteFilePost(request):
    file_id = request.POST.get('id')
    file_path = request.POST.get('path')
    file_in_db = FileInStorage.objects.get(id=file_id)
    deleted_file = DeletedFile(
        file_name=file_in_db.file_name,
        file_type=file_in_db.file_type,
        del_date=str(datetime.now()).split()[0],
        del_time=str(datetime.now()).split()[1].split('.')[0]
        )
    deleted_file.save()
    # Если файл был выбран до удаления, то убрать из сессии
    if 'selected-files' in request.session:
        selected_files = request.session['selected-files']
        if selected_files:
            index = 0
            for selected_file in selected_files:
                if selected_file['id'] == file_id:
                    selected_files.pop(index)
                    request.session['selected-files'] = selected_files
                    break
                index += 1

    file_in_db.delete()  # удаление записи файла из бд
    os.remove(file_path)
    return JsonResponse({'status': 'done'}, status=200)


@login_required
def selectedFilesPost(request):
    # Возвращает все выбранные файлы
    if 'selected-files' in request.session:
        selected_files = request.session['selected-files']
        return JsonResponse({'files': selected_files}, status=200)
    else:
        return JsonResponse({'files': []}, status=200)


@login_required
def cancelSelectingFilesPost(request):
    if request.method == 'POST':
        request.session['selected-files'] = []
        return redirect('/performancetech/')


@login_required
def chooseFilePost(request):
    # Если файл уже выбран - отменить выбор, в ином случае - выбрать файл
    file_id = request.POST.get('id')

    dir_path = request.POST.get('path')
    file_path = '/'+'/'.join('/'.join(dir_path.split('\\')[4:]).split('/')[1:])

    file_name = request.POST.get('name')
    file_type = request.POST.get('type')
    # Если уже выбирались файлы ранее
    if 'selected-files' in request.session:
        # Если уже файлы выбирались ранее
        selected_files = request.session['selected-files']
        index = 0
        if len(selected_files) != 0:  # 0, если все выборы были отменены
            for selected_file in selected_files:
                if selected_file['id'] == file_id:
                    # Необходимо вернуть unselect,
                    # а также удалить элемент из списка
                    selected_files.pop(index)
                    request.session['selected-files'] = selected_files
                    return JsonResponse(
                        {'action': 'unselect', 'id': file_id},
                        status=200)
                index += 1
            # Если данный объект не был найден, то добавляем его в сессию
            selected_files.append(
                {
                    'id': file_id,
                    'path': file_path,
                    'name': file_name,
                    'type': file_type
                })
            request.session['selected-files'] = selected_files
            return JsonResponse({'action': 'select'}, status=200)
        else:  # если объект в сессии есть, но он пуст
            request.session['selected-files'] = [
                {
                    'id': file_id,
                    'path': file_path,
                    'name': file_name,
                    'type': file_type
                }]
            return JsonResponse({'action': 'select'}, status=200)
    else:
        # Если ранее файлы не выбирались. В любом случае будет select
        request.session['selected-files'] = [
            {
                'id': file_id,
                'path': file_path,
                'name': file_name,
                'type': file_type}]
        return JsonResponse({'action': 'select'}, status=200)


# Создание веб-показа или презентации
@login_required
def create_performance_view(request):
    context = {}
    if 'selected-files' in request.session:
        selected_files = request.session['selected-files']
        selected_files_count = len(selected_files)
        if selected_files_count > 0:
            context['selected_files_count'] = selected_files_count
    context['active'] = 'createperformance'
    # Создание веб-презентации
    if request.method == 'POST':
        form = CreateWebPresentation(request.POST)
        if form.is_valid():
            presentation_name = request.POST.get('performanceName')
            notes = None
            if 'performanceNotes' in request.POST:
                notes = request.POST.get('performanceNotes')
            presentation_in_db, was_created = WebPresentation.objects\
                .get_or_create(
                    name=presentation_name,
                    is_active=True,
                    defaults={
                        # Поля для заполнения в случае отсутствия совпадений
                        'creation_date': str(datetime.now()).split()[0],
                        # задается при прогрузке страницы
                        'files': selected_files,
                        'files_count': len(selected_files),
                        'notes': notes
                        }
                    )
            if not was_created:
                if presentation_in_db.is_active:
                    context['error'] = (
                        'Активный показ с таким именем '
                        'уже существует'
                        )
                else:
                    context['message'] = 'Показ успешно создан'

    active_presentations = WebPresentation.objects.filter(is_active=True)
    if len(active_presentations):
        # Если есть активные показы - отобразить
        context['active_presentations'] = active_presentations
    return render(request, 'performancetech/create_perf.html', context=context)


@login_required
def show_presentation_view(request, id):
    context = {}
    context['active'] = 'createperformance'
    # Страница показа, параметр id - id показа
    presentation = WebPresentation.objects.get(id=id)
    if presentation:
        context['presentation'] = presentation
        if not presentation.is_active:
            # Пометка в верхней части страницы
            context['message'] = 'Презентация была помещена в архив'
        # формирует список словарей из строки таблицы
        presentation_files = eval(presentation.files)
        context['files'] = presentation_files
        context['files_count'] = len(presentation_files)
        if 'pm' in request.GET:
            # pm - метод показа, если img, то выдается галерея фото, если audio
            # то галерея звуков
            url_arg = request.GET.get('pm')
            if url_arg == 'images':
                # Вернуть страницу с изображениями
                img_count = 0
                for presentation_file in presentation_files:
                    if presentation_file['type'] == 'images':
                        img_count += 1
                if img_count > 0:
                    context['images_count'] = img_count
                else:
                    context['gallery_message'] = \
                        'Изображения не были добавлены'
                return render(
                    request,
                    'performancetech/images_gallery.html',
                    context=context
                )
            elif url_arg == 'audio':
                # Вернуть страницу с аудио-галереей
                audio_count = 0
                for presentation_file in presentation_files:
                    if presentation_file['type'] == 'audio':
                        audio_count += 1
                if audio_count == 0:
                    context['gallery_message'] = 'Аудиофайлы не были добавлены'
                return render(
                    request,
                    'performancetech/audio_gallery.html',
                    context=context
                )
    else:
        # Если веб-презентация не найдена -
        # возвращается страница для создания показов
        return redirect('/performancetech/create-performance')
    return render(
        request,
        'performancetech/presentation_page.html',
        context=context
        )


@login_required
def deletePresentationPost(request):
    if request.method == 'POST':
        presentation_id = int(request.POST.get('presentationID'))
        WebPresentation.objects.filter(id=presentation_id)\
            .update(is_active=False)
        return redirect('/performancetech/create-performance')


# ИСТОРИЯ ВЗАИМОДЕЙСТВИЯ С ФАЙЛАМИ, ПОКАЗАМИ
@login_required
def history_view(request):
    context = {}
    context['active'] = 'historypage'

    # История для файлов

    loaded_files = LoadedFile.objects.all()\
        .order_by('-load_date').order_by('-load_time')
    deleted_files = DeletedFile.objects.all()\
        .order_by('-del_date').order_by('-del_time')
    del_files_history = []
    load_files_history = []

    for loaded_file in loaded_files:
        load_files_history.append(
            {
                'name': loaded_file.file_name,
                'type': loaded_file.file_type,
                'date': loaded_file.load_date,
                'time': loaded_file.load_time,
                'section': loaded_file.section_name,
            }
        )
    for deleted_file in deleted_files:
        del_files_history.append(
            {
                'name': deleted_file.file_name,
                'type': deleted_file.file_type,
                'date': deleted_file.del_date,
                'time': deleted_file.del_time,
            }
        )
    context['load_files_history'] = load_files_history
    context['del_files_history'] = del_files_history

    # История для показов
    performances = WebPresentation.objects.all().order_by('-creation_date')
    performances_history = []
    for performance in performances:
        performances_history.append(
            {
                'date': performance.creation_date,
                'name': performance.name,
                'files_count': performance.files_count
            }
        )

    context['performances_history'] = performances_history
    return render(
        request,
        template_name='performancetech/history.html',
        context=context
        )


def all_notes_view(request):
    context = {}
    context['active'] = 'notespage'

    if request.method == 'POST':
        form = CreateNote(request.POST)
        if form.is_valid():
            date_now = str(datetime.now()).split()[0]
            time_now = str(datetime.now()).split()[1].split('.')[0]
            note_text = request.POST.get('notesInput')
            note_name = request.POST.get('nameInput')
            new_note = UserNote(
                note_name=note_name,
                note_text=note_text,
                creation_date=date_now,
                creation_time=time_now
            )
            new_note.save()
            context['success_message'] = 'Заметка успешно добавлена'
        else:
            context['error_message'] = 'Не удалось добавить заметку'

    # Отображение всех заметок
    all_notes = UserNote.objects.all().filter(is_active=True)
    if all_notes:
        context['notes'] = all_notes

    return render(
        request,
        template_name='performancetech/all_notes.html',
        context=context
        )


def notes_page_view(request, notes_id):
    this_note_in_db = UserNote.objects.all().filter(id=notes_id)
    context = {}
    context['active'] = 'notespage'

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'del':
            # Отправка заметки в архив
            this_note_in_db.update(is_active=False)
            return redirect('/performancetech/notes')
        elif action == 'change':
            # Редактирование заметки
            context['edit_mode'] = True
        elif action == 'apply-edit':
            changed_text = request.POST.get('changed-text')
            this_note_in_db.update(note_text=changed_text)

        elif action == 'cancel-edit':
            return redirect(f'/performancetech/notes/{notes_id}')

    if this_note_in_db:
        this_note = this_note_in_db[0]
        if not this_note.is_active:
            context['message'] = 'Заметка была помещена в архив'
        else:
            context['not_deleted_note'] = True
        context['note'] = this_note
        context['content_lines'] = this_note.note_text.split('\n')
        return render(
            request,
            template_name='performancetech/notes_page.html',
            context=context
        )
    else:
        return redirect('/performancetech/notes')
