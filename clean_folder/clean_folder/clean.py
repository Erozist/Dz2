import re
import os
import sys
import shutil
from pathlib import Path


UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")

TRANS = {}

for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()


def normalize(name: str) -> str:
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', '_', new_name)

    if extension == [''] or extension == []:
        return f"{new_name}"
    return f"{new_name}.{'.'.join(extension)}"


category_files = {
    'video': ('AVI', 'MP4', 'MOV', 'MKV'),
    'audio': ('MP3', 'OGG', 'WAV', 'AMR'),
    'documents': ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'),
    'images': ('JPEG', 'PNG', 'JPG', 'SVG'),
    'archives': ('ZIP', 'GZ', 'TAR'), }

registered_extensions = {}
video = []
audio = []
documents = []
images = []
archives = []
folders = list()
archives = list()
others = list()
unknown = set()
extensions = set()


for key, value in category_files.items():
    for exten in value:
        globals()[f"{key}_{exten.lower()}_files"] = list()
        registered_extensions.update(
            zip([exten], [globals()[f"{key}_{exten.lower()}_files"]]))

        video.append(
            globals()[f"{key}_{exten.lower()}_files"]) if key == "video" else ...
        audio.append(
            globals()[f"{key}_{exten.lower()}_files"]) if key == "audio" else ...
        documents.append(
            globals()[f"{key}_{exten.lower()}_files"]) if key == "documents" else ...
        images.append(
            globals()[f"{key}_{exten.lower()}_files"]) if key == "images" else ...
        archives.append(
            globals()[f"{key}_{exten.lower()}_files"]) if key == "archives" else ...


def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()


def scan(folder):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('video', 'audio', 'images', 'documents', 'archives',  'others'):
                folders.append(item)
                scan(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name

        if not extension:
            others.append(new_name)

        else:
            try:
                container = registered_extensions[extension]
                extensions.add(extension)
                container.append(new_name)

            except KeyError:
                unknown.add(extension)
                others.append(new_name)


def handle_file(path, root_folder, dist):
    target_folder = root_folder/dist
    target_folder.mkdir(exist_ok=True)
    path.replace(target_folder/normalize(path.name))


def handle_archive(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)
    del_folder = root_folder/path
    new_name = normalize(path.name.replace(
        ".zip", '').replace(".tar", '').replace(".gz", ''))

    archive_folder = target_folder / new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path.resolve()),
                              str(archive_folder.resolve()))

    except OSError:
        shutil.rmtree(archive_folder)
        os.remove(del_folder)
        return

    path.unlink()


def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass


def main():
    folder_path = Path(sys.argv[1])
    print(folder_path)
    scan(folder_path)

    # відеофайли ('AVI', 'MP4', 'MOV', 'MKV')
    for files in video:
        for file in files:
            handle_file(file, folder_path, "video")

        # музика ('MP3', 'OGG', 'WAV', 'AMR')
    for files in audio:
        for file in files:
            handle_file(file, folder_path, "audio")

        # зображення ('JPEG', 'PNG', 'JPG', 'SVG')
    for files in images:
        for file in files:
            handle_file(file, folder_path, "images")

        # документи ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX')
    for files in documents:
        for file in files:
            handle_file(file, folder_path, "documents")

        # архіви ('ZIP', 'GZ', 'TAR')
    for files in archives:
        for file in files:
            handle_archive(file, folder_path, "archives")
        # усі інші файли
    for file in others:
        handle_file(file, folder_path, "others")

    remove_empty_folders(folder_path)

    path = sys.argv[1]
    with open(f"{path}/Resume.txt", 'w+', encoding='utf-8') as file:
        file.write("Video: {}\n".format(
            " *|* ".join(([file.name for files in video for file in files]))))
        file.write("Audio: {}\n".format(
            " *|* ".join(([file.name for files in audio for file in files]))))
        file.write("Images: {}\n".format(
            " *|* ".join(([file.name for files in images for file in files]))))
        file.write("Documents: {}\n".format(
            " *|* ".join(([file.name for files in documents for file in files]))))
        file.write("Archives: {}\n".format(
            " *|* ".join(([file.name for files in archives for file in files]))))
        file.write("Others: {}\n".format(
            " *|* ".join(([file.name for file in others]))))
        file.write("Known extensions: {}\n".format(extensions))
        file.write("Unknown extensions: {}\n".format(unknown))



if __name__ == '__main__':
    main()

