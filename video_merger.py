import argparse
import json
import os
import random
import subprocess
import sys

video_list = 'video.txt'
audio_list = 'audio.txt'
temp_dir = 'merge_temp'
temp_video = 'temp.mp4'
temp_audio = 'temp.aac'


def main(args):
    des_file = args.d if args.d else 'output.mp4'

    input_video = get_files(args.videos)
    if not input_video:
        exit('视频文件路径错误')

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
        print(' > 开始重编码视频')
        scaled_videos = scale_videos(width, height, input_video)
        if not scaled_videos:
            exit('重编码视频时出错')
        final_video_segments = scaled_videos

    # TODO: 稳定运行后需要删除临时视频文件
    final_video = temp_video
    print(' > 开始合并视频片段')
    if len(final_video_segments) > 1:
        concat_videos(final_video_segments, temp_video)
    else:
        final_video = final_video_segments[0]

    audios = get_files(args.audio)
    if not audios:
        os.remove(des_file)
        os.rename(final_video, des_file)
        return

    video_duration = get_duration(temp_video)
    extend_audio_list = make_audio_list(audios, video_duration, args.random)
    print(' > 开始对音频转码')
    final_audio_segments = encode_audios(extend_audio_list)

    if final_audio_segments:
        print(' > 开始合并音频片段')
        final_audio = temp_audio
        if len(final_audio_segments) > 1:
            concat_audios(final_audio_segments, final_audio)
        else:
            final_audio = final_audio_segments[0]
        merge(final_video, final_audio, des_file)


def merge(video, audio, des):
    subprocess.run(f"ffmpeg -y -i {video} -i {audio} -map 0:v:0 -map 1:a:0 -c copy -shortest {des}")


def make_audio_list(audios, time, rand=True):
    def func(n):
        while True:
            index = [i for i in range(n)]
            if rand:
                random.shuffle(index)
            while len(index) > 0:
                yield index.pop()

    rest = time
    times = [get_duration(a) for a in audios]
    audio_time = list(zip(audios, times))
    audio_time = list(filter(lambda x: x[1] > 0, audio_time))
    res_list = []

    gen = func(len(audios))
    while rest > 0:
        num = next(gen)
        res_list.append(audio_time[num][0])
        rest -= audio_time[num][1]

    return res_list


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
        duration = float(d['streams'][0]['duration'])
    except (json.JSONDecodeError, AttributeError):
        pass

    return duration


def concat_videos(videos: list, des: str, temp=video_list) -> bool:
    if not videos:
        return True

    make_file(videos, temp)
    task = subprocess.run(f"ffmpeg -y -f concat -safe 0 -i {temp} -c copy {des}", shell=True)
    return task.returncode == 0


def concat_audios(audios: list, des: str, temp=audio_list) -> bool:
    if not audios:
        return True

    make_file(audios, temp)
    task = subprocess.run(f"ffmpeg -y -f concat -safe 0 -i {temp} -c copy {des}", shell=True)
    return task.returncode == 0


def scale_videos(width, height, videos, temp_folder=temp_dir):
    args = ['-vf', f'scale=(iw*sar)*min(1280/(iw*sar)\\,720/ih):ih*min(1280/(iw*sar)\\,720/ih), pad=1280:720:('
                   f'1280-iw*min(1280/iw\\,720/ih))/2:(720-ih*min(1280/iw\\,720/ih))/2',
            '-y']
    ext = get_ext(temp_video)

    return trans_media(videos, args, ext, temp_folder)


def encode_audios(audios, temp_folder=temp_dir):
    args = ['-c:a', 'aac', '-y']
    ext = get_ext(temp_audio)
    return trans_media(audios, args, ext, temp_folder)


def get_ext(file):
    i = file.rindex('.')
    return file[i + 1:]


def trans_media(files, cmd, ext, temp_folder=temp_dir):
    num, res, cache = 0, [], {}
    for file in files:
        if file in cache:
            res.append(cache[file])
        else:
            num += 1
            temp_file = os.path.join(temp_folder, str(num).zfill(4)) + '.' + ext
            full_cmd = ['ffmpeg', '-i', file]
            full_cmd.extend(cmd)
            full_cmd.append(temp_file)
            subprocess.run(full_cmd, shell=True)

            res.append(temp_file)
            cache.update({file: temp_file})
    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='合并视频并替换视频声音.')
    parser.add_argument('videos', metavar='video file/dir', nargs='+',
                        help='视频文件或文件夹')
    parser.add_argument('audio', metavar='audio file/dir', nargs=1,
                        help='声音文件或文件夹(若声音文件不存在则使用原视频声音)')
    parser.add_argument('-s', '--scale', metavar='video resolution',
                        help='导出文件分辨率(默认为所有视频中最大的分辨率): 如1280:720')
    parser.add_argument('-d', metavar='dest file',
                        help='导出文件路径(默认为当前目录下output.mp4)')
    parser.add_argument('-r', '--raw', default=False, action='store_true',
                        help='不进行重编码,快速合并(默认为进行重编码)')
    parser.add_argument('-a', '--random', default=True, action='store_false',
                        help='音频拼接时是否乱序(默认为乱序)')

    arg = parser.parse_args()
    main(arg)
