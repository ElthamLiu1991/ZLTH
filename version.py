import os
import time

main_version = '1'
major_version = '1'
minor_version = '0'


if __name__ == '__main__':
    if not os.path.exists('./version/'):
        os.mkdir('./version')
    try:
        with open('./version/version.txt', 'r+') as f:
            versions = f.read().split('.')
            f.seek(0)
            f.truncate()
            new_version = int(versions[2])+1
            f.write(main_version + '.' + major_version + '.' + str(new_version))
    except Exception as e:
        with open('./version/version.txt', 'w+') as f:
            f.write(main_version + '.' + major_version + '.' + minor_version)
