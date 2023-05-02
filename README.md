# Скачивание книг с сайта tululu

Данный репозитарий представляет собой набор скриптов, которые скачаваеют книги с сайта https://tululu.org/

### Как установить

Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```

### Пример запуска

Ниже представлен примеры запуска скриптов.
Для скачивания книг по id подряд воспользуйтесь командой
```commandline
> python.exe .\main.py --start_id 5 --end_id 10   
```
Для скачиваня книг жанра фантастики воспользуйтесь командой
```commandline
> python.exe .\parse_tululu_category.py --start_page 700 --end_page 701 
```
Ключи для .\main.py
```commandline
  -h, --help                  show this help message and exit
  --start_id START_ID         First book ID
  --end_id END_ID             Last book ID-1
  --skip_imgs                 Skip images downloading
  --skip_txt                  Skip book text downloading
  --dest_folder DEST_FOLDER   Destination folder

```
Ключи для parse_tululu_category.py
```commandline
  -h, --help                 show this help message and exit
  --start_page START_PAGE    start page number. Default value: 1
  --end_page END_PAGE        end page number. Default value: None
  --skip_imgs                Skip images downloading
  --skip_txt                 Skip book text downloading
  --json_path JSON_PATH      Path to json file
  --dest_folder DEST_FOLDER  Destination folder
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).