import argparse
import os

video_list = 'video.txt'
input_audio = 'audio.txt'
temp_video = 'temp.mp4'
temp_dir = 'merge_temp'


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
parser.add_argument('-s', '--scale', metavar='video resolution', required=True,
                    help='导出文件分辨率: 如1280:720')
parser.add_argument('-d', metavar='dest file', nargs='?',
                    help='导出文件路径(默认为当前目录)')

args = parser.parse_args()
des_file = args.d if args.d else 'output.mp4'

input_video = get_files(args.videos)
if not input_video:
    exit('视频文件路径错误')

# TODO: 未设置分辨率时实现分辨率自动配置，取视频文件中最大分辨率
width, height = map(int, args.scale.split(':'))

if os.path.exists(temp_dir):
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
else:
    os.mkdir(temp_dir)
    
num = 1
for v in input_video:
    temp_file = temp_dir + os.path.sep + str(num).zfill(4) + '.mp4'
    os.system(f'ffmpeg -i {v} -vf "scale=(iw*sar)*min({width}/(iw*sar)\\,{height}/ih):ih*min({width}/(iw*sar)\\,'
              f'{height}/ih), pad={width}:{height}:({width}-iw*min({width}/iw\\,{height}/ih))/2:({height}'
              f'-ih*min({width}/iw\\,{height}/ih))/2" {temp_file}')
    num += 1

mV = make_file([temp_dir], video_list)
# TODO: 稳定运行后需要删除临时视频文件
os.system(f"ffmpeg -y -f concat -safe 0 -i {video_list} -c copy {temp_video}")

# TODO: 背景音乐是否需要和视频一样支持合并（合并时可以乱序）
audios = get_files(args.audio)
if audios:
    os.system(f"ffmpeg -y -i {temp_video} -i {audios[0]} -map 0:v:0 -map 1:a:0 -c copy {des_file}")
