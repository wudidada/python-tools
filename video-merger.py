import argparse
import os

input_video = 'video.txt'
input_audio = 'audio.txt'
temp_file = 'temp.mp4'


def get_files(sources):
    filenames = []
    for source in sources:
        if not os.path.exists(source):
            return []
        if os.path.isfile(source):
            filenames.append(source)
        else:
            files = os.listdir(source)
            for file in files:
                fullname = source + os.path.sep + file
                if os.path.isfile(fullname):
                    filenames.append(fullname)
    return filenames


def make_file(sources, output_file):
    filenames = get_files(sources)
    if not filenames:
        return False

    with open(output_file, 'w') as f:
        for fn in filenames:
            f.write(f"file '{fn}'\n")
    return True


parser = argparse.ArgumentParser(description='合并视频并替换视频声音.')
parser.add_argument('videos', metavar='video file/dir', nargs='+',
                    help='视频文件或文件夹')
parser.add_argument('audio', metavar='audio file/dir', nargs=1,
                    help='声音文件或文件夹(若声音文件不存在则使用原视频声音)')
parser.add_argument('-d', metavar='dest file', nargs='?',
                    help='导出文件路径(默认为当前目录)')

args = parser.parse_args()
des_file = args.d if args.d else 'output.mp4'

mV = make_file(args.videos, input_video)
if not mV:
    exit('视频文件路径错误')
os.system(f"ffmpeg -y -f concat -safe 0 -i {input_video} -c copy {temp_file}")

# TODO: 背景音乐是否需要和视频一样支持合并（合并时可以乱序）
audios = get_files(args.audio)
if audios:
    os.system(f"ffmpeg -y -i {temp_file} -i {audios[0]} -map 0:v:0 -map 1:a:0 -c copy {des_file}")
