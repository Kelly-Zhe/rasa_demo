# # import subprocess

# # from gtts import gTTS 

# # mytext = "你好"

# # language = 'zh'

# # myobj = gTTS(text = mytext, lang = language)

# # myobj.save("welcome.mp3")

# # subprocess.call(['mpg321','welcome.mp3','--play-and-exit'])
import pyttsx3

engine = pyttsx3.init()#初始化
engine.say(u"汉语：我爱你")#汉语
engine.say(u"英 语：I love you")#英语
engine.runAndWait()