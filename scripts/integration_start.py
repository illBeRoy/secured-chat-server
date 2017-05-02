#!/usr/bin/env python
import os
import shutil
import subprocess


if __name__ == '__main__':
    executable_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
    assets_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tmp')
    server_port = 3000

    try:
        shutil.rmtree(assets_path)
    except:
        pass

    os.makedirs(assets_path)

    subprocess.Popen('source ./venv/bin/activate && ./start.py -p {0} -db "sqlite:///{1}"'.format(server_port,
                                                                                                  os.path.join(assets_path, 'db.sqlite')),
                     shell=True,
                     cwd=executable_path).communicate()
