import os
from os.path import expanduser, join
import sys

from transf import Formatter

def main():
    """"""
    if len(sys.argv) < 2:
        print("please specify folder contain log folders")
        return
    base_folder = expanduser(sys.argv[1])
    folders = os.listdir(sys.argv[1])
    for f in folders:
        p = join(base_folder, f)
        if os.path.isdir(p):
            try:
                formatter = Formatter(p)
                formatter.do()
            except Exception as e:
                print('error while parsing', p)
                print(e)

if __name__ == "__main__":
    main()