import os
import json
import youtube_dl
import re
import pyperclip
import configparser
import sys
proxy = {}


def init():
    global proxy
    if 'config.ini' not in os.listdir():
        print('检测到config文件不存在，接下来将引导生成配置文件')
        config = configparser.ConfigParser()
        proxy = input('请输入需要使用的代理地址，留空则不使用代理：')
        config['GENERAL'] = {'proxy': proxy}
        config.write(open('config.ini', 'w'))
        print('初始化完毕，请重新运行')
        exit()
    config = configparser.ConfigParser()
    config.read('config.ini')
    if config['GENERAL']['proxy']:
        proxy = {'proxy': config['GENERAL']['proxy']}


def get_format(url):
    ydl = youtube_dl.YoutubeDL(params=proxy)
    with ydl:
        result = ydl.extract_info(
            url,
            download=False,  # We just want to extract the info
        )

    if 'entries' in result:
        # Can be a playlist or a list of videos
        video = result['entries'][0]
    else:
        # Just a video
        video = result

    form = ydl.list_formats(video)
    return form


def downloader(jobs):
    download_params = proxy
    ytdl = youtube_dl.YoutubeDL(params=download_params)
    subdl = youtube_dl.YoutubeDL(params=download_params)
    # print(jobs)
    for job in jobs:
        file_name = job['file_name']
        # subtitle_name = re.search(r'(?<= --skip-download -o \").+?%\(container\)s\.vtt', job).group(0)
        download_format = job['format']
        url = job['url']
        print('正在下載：{}，格式爲：{}'.format(url, download_format))
        download_params.update(
            {'format': download_format, 'outtmpl': file_name})
        sub_params = download_params | {'writesubtitles': 'True', 'allsubtitles': 'True', 'skip_download': 'True'}
        del sub_params['format']
        # print(download_params)
        ytdl.params = download_params
        subdl.params = sub_params
        while True:
            try:
                ytdl.download([url])  # 下载视频
                subdl.download([url])  # 下载字幕
            except youtube_dl.utils.DownloadError as d:
                if str(d) == 'ERROR: requested format not available':
                    output = '请求格式不存在，跳过执行：{}\n'.format(url)
                    print(output)
                    with open('short.log', 'a') as log:
                        log.write(output)
                    break
                else:
                    output = '下载失败，正在重试：{}\n'.format(url)
                    print(output)
                    with open('short.log', 'a') as log:
                        log.write(output)
            else:
                break

    return False


def main():
    proxy_server = '--proxy ' + proxy['proxy'] if proxy else ''
    raw = input('please give me a imdb name:')
    if raw == 'download':
        with open('short.json', 'r', encoding='utf-8') as short:
            jobs = json.load(short)
        return downloader(jobs)
    url = input('please give me the vimeo url:')
    movie_name = re.search(r'(.+)\s+(\d+)', raw)
    print(get_format(url))
    option = input('\n请输入需要下载的格式的id，用英文逗号隔开：\n')
    zero_day = '{}.{}.%(height)sp.WEB-DL.x264-HLW.%(container)s'.format(movie_name.group(1).rstrip().replace(' ', '.'),
                                                                        movie_name.group(2))
    download = 'youtube-dl -f {} -o "{}" {}  {} && youtube-dl --all-subs  --skip-download -o "{}.vtt" {} {}\n\n'.format(
        option, zero_day, url, proxy_server, zero_day, url, proxy_server)
    print(download)
    pyperclip.copy(download)
    job = {'file_name': zero_day, 'format': option, 'url': url, 'command': download}
    if 'short.json' in os.listdir():
        with open('short.json', 'r') as s:
            jobs = json.load(s)
    else:
        jobs = []

    with open('short.json', 'w') as s:
        jobs.append(job)
        json.dump(jobs, s)
    return True


if __name__ == '__main__':
    if os.path.basename(sys.argv[0]) != '爆筋的精液超多且持久的大黑硬鸡巴.pyc':
        input('检测到文件名错误，拒绝执行。文件名应为：\n爆筋的精液超多且持久的大黑硬鸡巴.pyc')
        exit()
    init()
    loop = True
    while loop:
        loop = main()
