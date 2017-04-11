from PIL import Image
import os, sys
from app import app
import glob2


def generate_thumbnail(infile_name, root_directory):
    size = 256, 256
    target_file = os.path.join(root_directory, 'uploads')
    found_file = glob2.glob(target_file)
    for name in os.listdir(target_file):
        if infile_name in name:
            found_file = name
    try:
        path = os.path.join(target_file, found_file)
        save_path = os.path.join(target_file + '/', infile_name)
        outfile = Image.open(path)
        outfile.thumbnail(size)
        outfile.save(save_path + '_thumbnail.png')
    except Exception as e:
        print("Ran into an error creating a thumbnail")
        print(e)
