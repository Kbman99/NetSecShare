from PIL import Image
import os
import sys
from app import app


def generate_thumbnail(infile_name):
    try:
        size = 206.67, 256.29
        target_dir = app.config['UPLOAD_PATH']
        # found_file = ''
        # for name in os.listdir(target_dir):
        #     if infile_name in name:
        #         found_file = name

        file_path = os.path.join(target_dir + '/', infile_name)
        save_path = os.path.join(target_dir + '/', os.path.splitext(infile_name)[0])
        print(target_dir, file=sys.stderr)
        print(infile_name, file=sys.stderr)
        outfile = Image.open(file_path)
        outfile.thumbnail(size)
        outfile.save(save_path + '_thumbnail.png')
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e), e, file=sys.stderr)
        print(e)
