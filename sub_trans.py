import os

import pysubs2
from pysubs2 import SSAStyle
from zhconv import convert

DEFAULT_STYLE = SSAStyle(fontname='STKaiti', fontsize=18, outline=1, shadow=1)
OUTPUT_DIR = 'K:\\书包\\自制字幕'


def main():
    while (file := input('srt path: ')) != '':
        trans(file)


def trans(file):
    try:
        subs = pysubs2.load(file)
    except UnicodeDecodeError:
        try:
            subs = pysubs2.load(file, 'gbk')
        except UnicodeDecodeError:
            subs = pysubs2.load(file, 'utf-16')
    subs.styles['Default'] = DEFAULT_STYLE
    subs.info['PlayResX'] = '384'
    subs.info['PlayResY'] = '288'
    subs.info['ScaledBorderAndShadow'] = 'no'
    for line in subs:
        line.text = convert(line.text, 'zh-cn')
    subs.save(output_file(file))


def output_file(file):
    filename = os.path.basename(file)
    return OUTPUT_DIR + os.path.sep + os.path.splitext(filename)[0] + '.ass'


if __name__ == '__main__':
    main()
