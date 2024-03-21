from openai import OpenAI
import urllib.request
import json
from pydub import AudioSegment
import os
import assemblyai as aai
import winsound

# Авторизация в ИИ
client = OpenAI(api_key="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")
aai.settings.api_key = "7c2fad12590a42d6802f149b24be318b"

# Делает транскрипция читабельной
def normalizeTranscript(obj):
    arr = obj.words
    lastSpeaker = 0
    mess = ''
    names = {'1':"Абонент","2":'Оператор'}
    for word in arr:
        if word.speaker != lastSpeaker:
            lastSpeaker = word.speaker
            mess += f'\n {names[lastSpeaker]} {word.text}'
        else:
            mess+=f" {word.text}"

    return mess

# Конвертирует двухканельный аудиофайл в моно для уменьшения веса в хранилище данных
def convertToMono(fileName):
    audio = AudioSegment.from_file(fileName)
    mono = audio.set_channels(1)
    mono.export(f'{fileName}_mono.wav',format='wav')
    os.remove(fileName)

# Принимает JSON через API и делает его читаемым
def readChats(url):
     with urllib.request.urlopen(url) as response:
         body_json = response.read()

     body_dict = json.loads(body_json)

     chats = []

     for chat in body_dict['data']:
         all_messages = ''
         for messaging in chat['messages']:
             all_messages += f"{messaging['type'] + ': ' + messaging['name']} \n {messaging['message']} \n\n"
         chats.append(all_messages)
         
     return chats

# Промпт в ChatGPT
analyze_requests = [{"role": "system", "content": """
Ты анализируешь диалоги оператора колл-цента компании триолан
Твоя задача:
провести симантический анализ диалога по таким критериям:
Краткое содержание:
*выдать краткое содержание всего диалога*

Тема диалога: *тут ты выявляешь основную тему диалога, выбираешь только из списка тем:
-Новое подключение
-Повторная активация услуги
-Ремонт
-Авария
-Финансы
-Откдюыение
-Обслуживание
-Другое*
                     
Анализ настроения:
	Общее: *тут ты анализируешь основное настроение диалога*
	Оператор: *тут ты анализируешь настроение оператора*
	Абонент: *тут ты анализаруешь настроение абонента*

Ключевые моменты диалога:
*тут ты выявляешь основные моменты диалога*

Ошибки оператора:
 *если ошибок нет оставь поле пустым*
             
Звучал ли номер лицевого счёта или адресс проживания абонента в диалоге:
*Номер лицевого счёта/номер договора состоит из 7 или 15 цифр, адресс может звучать в любом контексте, ответ: да или нет*

Ключевые слова:
 *тут набор клюевых слов в разговоре*
             
Портрет:
*создай психологический портрет абонента*
                     
Оценка оператора:
*от 1 до 10*
                     
Решена ли проблема абонента:
*да или нет*
                     
Рекомендации к следующему шагу:
*тут ты даёшь ответ что нужно сделать после диалога оператору, если ещё что-то требуется*
             
Создана ли заявка на мастера:
*ответ только Да или Нет*
                     
Нужно ли обратить внимание на диалог для более детального диалога и коррекции оператора: *да или нет*

"""},{}]

# Для удобства разделения анализа чатов и аудио
input = str(input("1- Анализ чатов\n2- Анализ телефонии\n"))

# Записываются ответы модели
answers = []

# Записываются транскрипты пдготовленные при помощи AssemblyAI
transcriptArray=[]

# Формируется запрос для модели
if input == "1":
    dialogs = readChats("https://oc.triolan.com/tApi/ServiceDummy/GetDummyChats")
    for chat in dialogs:
        analyze_requests[1]={'role':'user','content':chat}
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=analyze_requests,
            max_tokens=4096,
            temperature=.6
        )
        answers.append(response.choices[0].message.content)
else:
    dialogs = ['1_.wav','2_.wav','3_.wav','4_.wav']
    config = aai.TranscriptionConfig(language_code="uk", audio_start_from=3000,dual_channel=True)
    transcriber = aai.Transcriber(config=config)
    for i in range(0,len(dialogs)):
        normalyzeTranscriptText=''
        transcript = transcriber.transcribe(dialogs[i])

        if transcript.status == aai.TranscriptStatus.error:
            print(transcript.error)
        else:
            file=open(f"{dialogs[i]}.txt",'a',encoding="UTF-8")
            for paragraph in transcript.get_paragraphs():
                normalyzeTranscriptText+=normalizeTranscript(paragraph)
            transcriptArray.append(normalyzeTranscriptText)

        analyze_requests[1]={'role':'user','content':normalyzeTranscriptText}
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=analyze_requests,
            max_tokens=4096,
            temperature=.6
        )
        answers.append(response.choices[0].message.content)


# Запись в файл
for i in range(0, len(answers)):
    file=open(f'Analis{i+100}.txt','w',encoding="UTF-8")
    if input == '1':
        file.write(f'{dialogs[i]}\n******************************************************************************************************\n{answers[i]}')
    else:
        file.write(f'{transcriptArray[i]}\n******************************************************************************************************\n{answers[i]}')
        convertToMono(f'{i+1}_.wav')
    file.close()

# Звуковой эффект для удобства
winsound.MessageBeep(1)