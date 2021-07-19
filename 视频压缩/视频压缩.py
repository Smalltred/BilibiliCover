import os

NEW_RESOLUTION = '1920x1080'
NEW_FPS = '60'
NEW_BIT = '20M'

videos_input_list = []
videos_output_lsit = []

videos_input = ".\\input\\"
videos_output = ".\\output\\"

# 视频列表名称
videos_list = os.listdir(videos_input)
# 循环名称拼接
for videos_name in videos_list:
    ffmpeg_cmd = "ffmpeg -hwaccel cuvid -c:v h264_cuvid -i %s -r %s -c:v h264_nvenc -b:v %s %s" % (
         videos_input + videos_name, NEW_FPS, NEW_BIT,  videos_output + videos_name)
    os.system(ffmpeg_cmd)
os.system("pause")

