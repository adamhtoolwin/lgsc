import os
import glob
from tqdm import tqdm

import cv2
import argparse
import pandas as pd


def make_folder(folder):
    if not os.path.isdir(folder):
        os.makedirs(folder)


parser = argparse.ArgumentParser(
        description='Extract frames from CASIA-FASD videos.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument('video_folder', type=str, help='Folder to process videos.')
parser.add_argument('-t', '--file_type', type=str, help='File type of video.', default="avi")
parser.add_argument('-f', '--frames', type=int, help='Number of frames to extract.', default=99999)
parser.add_argument('-o', '--output_csv', type=str, help='File to output CSV label file.', default=None)
parser.add_argument('-l', '--labels_file', type=str, help='The file to refer to for the labels.', default=None)

args = parser.parse_args()

video_files = glob.glob(args.video_folder + "/*." + args.file_type)

img_folder = args.video_folder.rstrip("/") + "/imgs/"

make_folder(img_folder)

if args.labels_file is None:
    args.labels_file = "/root/datasets/casia-fasd/labels.txt"

if args.output_csv is None:
    args.output_csv = "/root/datasets/casia-fasd/labels.csv"

labels_df = pd.read_csv(args.labels_file, sep=" ")
data = {
    'path': [],
    'target': []
}

pbar = tqdm(video_files)
for video_file in pbar:
    video_folder_name = video_file.split("/")[-1].split(".")[0]

    label = labels_df.loc[labels_df['folder'] == video_folder_name].iloc[0].target
    pbar.set_description("Processing video %s " % video_folder_name)
    video_folder = img_folder + video_folder_name

    make_folder(video_folder)

    vidcap = cv2.VideoCapture(video_file)
    success, image = vidcap.read()
    count = 1
    while success and count <= args.frames:
        file_name = video_folder + "/%d.jpg" % count

        data['path'].append(file_name)
        data['target'].append(label)

        cv2.imwrite(file_name, image)  # save frame as JPEG file
        success, image = vidcap.read()
        # print('Read a new frame: ', success)
        count += 1

df = pd.DataFrame(data)
df.to_csv(args.output_csv, index=False)


