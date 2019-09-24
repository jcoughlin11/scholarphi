"""

This assumes that you already have a LaTeX source directory & it compiles correctly.



"""

import argparse

from typing import Optional, List

import os
import subprocess
import shutil
import bs4
import json

from pprint import pprint

import re

import numpy as np
import cv2
from imageio import imread, imsave
from explanations.explanations.bounding_box import bbs_for_color, find_connected_components, cluster_nearby_connected_components, merge_bbs
from explanations.explanations.image_diff import diff_two_images

from collections import namedtuple
Span = namedtuple('Span', 'start end text')

def find_all_math_tags(input_latex_file: str) -> List[Span]:
    with open(input_latex_file, "rb") as f:
        # Some files may cause a UnicodeDecodeError if read directly as text, e.g. '/net/nfs.corp/s2-research/figure-extraction/data/distant-data/arxiv/src/0001/cond-mat0001356/s10677c.tex'
        text = bs4.UnicodeDammit(f.read()).unicode_markup
        spans = [Span(matches.start(0), matches.end(0), text[matches.start(0):matches.end(0)]) for matches in re.finditer(r'(\$(.*?)\$)', text)]
        return spans


def call_pdflatex(input_latex_dir: str, output_latex_dir: str):
    pass

def rasterize_pdf(input_pdf_path: str, output_dir: str):
    """Rasterize a PDF using GhostScript.
    Command:
        gs -dGraphicsAlphaBits=4 -dTextAlphaBits=4 -dNOPAUSE -dBATCH -dSAFER -dQUIET -sDEVICE=png16m -r96 -sOutputFile=output1_inject/%04d.png -dBufferSpace=1000000000 -dBandBufferSpace=500000000 -sBandListStorage=memory -c 1000000000 setvmthreshold -dNOGC -dLastPage=50 -dNumRenderingThreads=4 -f output1_color/mainRecSys.pdf
    """
    # ghostscript requires a template string for the output path
    output_path_template = os.path.join(output_dir, "%04d.png")
    gs_args = [
        "gs",
        "-dGraphicsAlphaBits=4",
        "-dTextAlphaBits=4",
        "-dNOPAUSE",
        "-dBATCH",
        "-dSAFER",
        "-dQUIET",
        "-sDEVICE=png16m",
        "-r96",
        "-sOutputFile=" + output_path_template,
        "-dBufferSpace=%d" % int(1e9),
        "-dBandBufferSpace=%d" % int(5e8),
        "-sBandListStorage=memory",
        "-c",
        "%d setvmthreshold" % int(1e9),
        "-dNOGC",
        "-dLastPage=50",
        "-dNumRenderingThreads=4",
        "-f",
        input_pdf_path,
    ]
    subprocess.run(gs_args, check=False)

def diff_image(input_png_path1: str, input_png_path2: str, output_png_path: str):
    img1 = imread(input_png_path1)
    img2 = imread(input_png_path2)
    diff_img = diff_two_images(img1, img2)
    imsave(output_png_path, diff_img)

def compute_bounding_boxes(diff_png_path: str, input_png_for_bbox_overlay_path: str, output_dir: str):
    diff_img = imread(diff_png_path)

    # compute bounding boxes
    connected_components = find_connected_components(diff_img, lower=np.array([0, 0, 0]), upper=np.array([180, 255, 125]))
    level, clusters, d = cluster_nearby_connected_components(connected_components)
    bounding_boxes = [merge_bbs(cluster) for cluster in clusters]
    pprint(bounding_boxes)

    # overlay
    img_for_overlay = imread(input_png_for_bbox_overlay_path)
    for i, bb in enumerate(bounding_boxes):
        minX, minY, maxX, maxY = bb
        img_with_overlay = cv2.rectangle(img_for_overlay, (minX, minY), (maxX, maxY), (255, 0, 0))
        imsave(os.path.join(output_dir, f'{i}.png'), img_with_overlay)
    return bounding_boxes


if __name__ == '__main__':
    diff_image(input_png_path1='explanations/1909.08079_output_original/0003.png',
               input_png_path2='explanations/1909.08079_output_colorized/0003.png',
               output_png_path='explanations/1909.08079_output_diff/0003.png')

    compute_bounding_boxes(diff_png_path='explanations/1909.08079_output_diff/0003.png',
                           input_png_for_bbox_overlay_path='explanations/1909.08079_output_original/0003.png',
                           output_dir='explanations/')

