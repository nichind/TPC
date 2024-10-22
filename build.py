from shutil import copytree, copyfile, rmtree
from os import getcwd, listdir
from platform import system
import PyInstaller.__main__


def main():
    
    add_data = []
    venv_path = getcwd() + '/.venv'
    if system().lower() == 'windows':
        venv_path += '/Lib/site-packages'
    else:
        venv_path += '/lib/python3.11/site-packages'
    locales = listdir('./locales')
    for locale in locales:
        add_data.append(f'--add-data=./locales/{locale};locales')
    assets = listdir('./assets')
    for asset in assets:
        add_data.append(f'--add-data=assets/{asset};assets')
    add_data.append(f'--add-data={venv_path}/plyer;plyer')
    add_data.append('--add-data=./core/bot/handlers;core/bot/handlers')
    if system() == 'Windows':
        add_data.append(f'--add-data={venv_path}/winsdk;winsdk')
        add_data.append('--hidden-import=winsdk')
    add_data.append('--add-data=./core/pc;core/pc')
    add_data.append('--hidden-import=mss')
    add_data.append('--hidden-import=pynput')
    
    all_args = [
        '--onefile',
        '--windowed',
        '--noconsole',
        '--hidden-import=aiosqlite',
        '--hidden-import=plyer.platforms.win.notification',
        '--paths=.venv\Lib\site-packages',
        '--icon=./assets/ico.gif',
        '--name=TPC',
        *add_data,
        './main.py',
    ]
    
    if system().lower() == 'linux':
        all_args = [i.replace(';', ':') for i in all_args]   
    PyInstaller.__main__.run(all_args)

    
if __name__ == '__main__':
    main()
