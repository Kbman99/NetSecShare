from PIL import Image
import os, sys


def generate_thumbnail(infile_name, root_directory):
    size = 256, 256
    target_file = os.path.join(root_directory, 'uploads')
    for name in os.listdir(target_file):
        if infile_name in name:
            found_file = name
        else:
            found_file = None
    try:
        path = os.path.join(target_file, found_file)
        save_path = os.path.join(target_file + '/', infile_name)
        print(target_file, file=sys.stderr)
        print(infile_name, file=sys.stderr)
        outfile = Image.open(path)
        outfile.thumbnail(size)
        outfile.save(save_path + '_thumbnail.png')
    except Exception as e:
        print("Ran into an error creating a thumbnail")
        print(e)
