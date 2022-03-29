import os
import time

main_version = '1'
major_version = '1'
minor_version = '0'


if __name__ == '__main__':
    if not os.path.exists('./version/'):
        os.mkdir('./version')
    with open('./version/version.txt', 'w+') as f:
        f.write(main_version + '.' + major_version + '.' + minor_version + '.' + \
                time.strftime('%Y%m%d%H%M%S', time.localtime()))
