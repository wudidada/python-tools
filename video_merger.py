import argparse
import json
import os
import subprocess
import sys

video_list = 'video.txt'
input_audio = 'audio.txt'
temp_video = 'temp.mp4'
temp_audio = 'temp.aac'
temp_dir = 'merge_temp'


def main(args):
    des_file = args.d if args.d else 'output.mp4'

    input_video = get_files(args.videos)
    if not input_video:
        exit('视频文件路径错误')

    # TODO: 未设置分辨率时实现分辨率自动配置，取视频文件中最大分辨率
    if args.scale:
        width, height = map(int, args.scale.split(':'))
    else:
        width, height = auto_resolution(input_video)
    if not width or not height:
        exit('视频分辨率无效')

    if os.path.exists(temp_dir):
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))
    else:
        os.mkdir(temp_dir)

    final_video_segments = input_video
    if not args.raw:
        scaled_videos = scale_videos(width, height, input_video)
        if not scaled_videos:
            exit('重编码视频时出错')
        final_video_segments = scaled_videos

    # TODO: 稳定运行后需要删除临时视频文件
    merge_videos(final_video_segments, temp_video)

    # TODO: 背景音乐是否需要和视频一样支持合并（合并时可以乱序）
    audios = get_files(args.audio)
    if audios:
        os.system(f"ffmpeg -y -i {temp_video} -i {audios[0]} -map 0:v:0 -map 1:a:0 -c copy {des_file}")


def get_files(sources: list) -> list:
    filenames = []
    for source in sources:
        if not os.path.exists(source):
            return []
        if os.path.isfile(source):
            filenames.append(source)
        else:
            files = os.listdir(source)
            for file in files:
                fullname = os.path.join(source, file)
                if os.path.isfile(fullname):
                    filenames.append(fullname)
    return filenames


def make_file(sources: list, output_file) -> bool:
    filenames = get_files(sources)
    if not filenames:
        return False

    with open(output_file, 'w') as f:
        for fn in filenames:
            f.write(f"file '{fn}'\n")
    return True


def auto_resolution(videos: list) -> (int, int):
    res_w, res_h, max_res = 0, 0, 0
    for v in videos:
        w, h = get_hw(v)
        if not w or not h:
            print(f"get resolution failed : {v}", file=sys.stderr)
            continue
        if w * h > max_res:
            res_w, res_h, max_res = w, h, w * h
    return res_w, res_h


def get_hw(video):
    width, height = 0, 0
    res = subprocess.check_output(f'ffprobe -v error -show_entries stream=width,height -of json '
                                  f'-select_streams v:0 "{video}"')
    try:
        hw = json.loads(res)
        width = hw['streams'][0]['width']
        height = hw['streams'][0]['height']
    except (json.JSONDecodeError, AttributeError):
        pass

    return width, height


def get_duration(media):
    duration = 0
    res = subprocess.check_output(f'ffprobe -v error -show_entries stream=duration -of json '
                                  f'"{media}"')
    try:
        d = json.loads(res)
        duration = d['streams'][0]['duration']
    except (json.JSONDecodeError, AttributeError):
        pass

    return duration


def merge_videos(videos: list, des: str, temp=video_list) -> bool:
    make_file(videos, temp)
    task = subprocess.run(f"ffmpeg -y -f concat -safe 0 -i {temp} -c copy {des}", shell=True)
    return task.returncode == 0


def scale_videos(width, height, videos, temp_folder=temp_dir):
    scaled_files = []
    num = 1
    for v in videos:
        temp_file = temp_folder + os.path.sep + str(num).zfill(4) + '.mp4'
        os.system(f'ffmpeg -i "{v}" -vf "scale=(iw*sar)*min({width}/(iw*sar)\\,{height}/ih):ih*min({width}/(iw*sar)\\,'
                  f'{height}/ih), pad={width}:{height}:({width}-iw*min({width}/iw\\,{height}/ih))/2:({height}'
                  f'-ih*min({width}/iw\\,{height}/ih))/2" {temp_file}')
        num += 1
        scaled_files.append(temp_file)

    return scaled_files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='合并视频并替换视频声音.')
    parser.add_argument('videos', metavar='video file/dir', nargs='+',
                        help='视频文件或文件夹')
    parser.add_argument('audio', metavar='audio file/dir', nargs=1,
                        help='声音文件或文件夹(若声音文件不存在则使用原视频声音)')
    parser.add_argument('-s', '--scale', metavar='video resolution',
                        help='导出文件分辨率(默认为所有视频中最大的分辨率): 如1280:720')
    parser.add_argument('-d', metavar='dest file',
                        help='导出文件路径(默认为当前目录)')
    parser.add_argument('-r', '--raw', default=False, action='store_true',
                        help='不进行重编码,快速合并')

    arg = parser.parse_args()
    main(arg)
