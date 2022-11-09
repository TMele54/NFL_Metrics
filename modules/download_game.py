import urllib.request

game = "https://ok.ru/video/4573391293014?fromTime=5559"

urllib.request.urlretrieve(game, 'video_name.mp4')

