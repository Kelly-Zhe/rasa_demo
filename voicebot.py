import requests
import pyttsx3
import speech_recognition as sr 
# sender = input("你好，请问你叫什么？\n")

bot_message= ""
message=""

r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": "Hello"})
engine = pyttsx3.init()#初始化
engine.say(u"我爱你")#汉语
engine.runAndWait()

print("Bot says, ",end=' ')
for i in r.json():
    bot_message = i['text']
    print(f"{bot_message}")

engine.say(bot_message)
engine.runAndWait()
# myobj = gTTS(text=bot_message)
# myobj.save("welcome.mp3")
# print('saved')

while bot_message != "再见":

	r = sr.Recognizer()
	with sr.Microphone() as source:
		print("讲两句：")
		audio = r.listen(source)
		try:
			message = r.recognize_google(audio,language = "zh")
			print("你说：{}".format(message))
		except:
			print("不好意思没有识别出你在说什么玩意儿")
	
	if len(message) == 0 :
		continue
	print("正在发送信息...")

	r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": message})
	print("机器人说:", end=' ')
	for i in r.json():
		bot_message = i['text']
		print(f"{i['text']}")

	engine.say(bot_message)
	engine.runAndWait()