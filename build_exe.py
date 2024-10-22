from shutil import copytree, copyfile, rmtree
from os import getcwd, listdir
import PyInstaller.__main__


def main():
    
    add_data = []
    locales = listdir('locales')
    for locale in locales:
        add_data.append(f'--add-data=locales/{locale};locales')
    assets = listdir('assets')
    for asset in assets:
        add_data.append(f'--add-data=assets/{asset};assets')
    add_data.append(f'--add-data=.venv/Lib/site-packages/plyer;./plyer')
    
    PyInstaller.__main__.run([
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
    ])

    
if __name__ == '__main__':
    main()
