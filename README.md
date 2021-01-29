# 工具箱

## dianfei.py

电费计算，输入当月每日用电，计算出每日电费及总电费。

## video_merger.py

视频合并以及替换音轨。视频合并时一般情况下需要将视频重编码为相同分辨率，音频重编码为aac。视频调整分辨率时保持原有比例，多余部分添加黑边。在音频长度小于视频长度时，对音频进行拼接。

### 使用环境

1. python 3
2. ffmpeg，需将ffmpeg bin目录加入环境变量，能在命令行下使用`ffmpeg`命令

### 使用样例

#### 常用命令

```
python video_merger.py video music -d output.mp4	# 合并video目录下所有视频文件,并将视频声音替换为music目录下音频,输出文件为output.mp4
# 输入视频支持目录或文件名,可多项; 输入音频支持目录或文件,在视频文件后,只能一项。														
python video_merger.py -h							# 查看帮助

python video_merger.py video music -s 1920:1080		# 合成为1920x1080分辨率，输出文件为默认为output.mp4
python video_merger.py video none -s -r				# 不进行重编码直接将视频文件合并，且不替换视频原有声音。
# 在视频分享率相同时使用-r选项会极大加快合并速度；若指定的音频文件不存在则不替换音轨。
```

#### 命令详解

```
video_merger.py [-h] [-s video resolution] [-d dest file] [-r] [-a]
                       video file/dir [video file/dir ...] audio file/dir

positional arguments:
  video file/dir        视频文件或文件夹
  audio file/dir        声音文件或文件夹(若声音文件不存在则使用原视频声音)

optional arguments:
  -h, --help            show this help message and exit
  -s video resolution, --scale video resolution
                        导出文件分辨率(默认为所有视频中最大的分辨率): 如1280:720
  -d dest file          导出文件路径(默认为当前目录下output.mp4)
  -r, --raw             不进行重编码,快速合并(默认为进行重编码)
  -a, --random          音频拼接时是否乱序(默认为乱序)
```

