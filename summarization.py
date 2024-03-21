main_search = ["Создана ли заявка на мастера:", "Решена ли проблема абонента:","Тема диалога"]

obj = {
    "Создана ли заявка на мастера:":{
        "Да":0,
        "Нет":0
    },
    "Решена ли проблема абонента:":{
        "Да":0,
        "Нет":0
    },
    "Тема диалога":{
        "Новое подключение":0,
        "Повторная активация услуги":0,
        "Ремонт":0,
        "Авария":0,
        "Финансы":0,
        "Отключение":0,
        "Обслуживание":0,
        "Другое":0
    }
}

for i in range(0,100):
    file = open(f"Analis{i}.txt", "r",encoding="utf-8")
    text = file.read()

    for word in main_search:
        start_pos = text.find(word) # положение первого индекса искуемого предложения

        if start_pos != -1: # если позиция найдена
            end_pos = text.find('\n', start_pos) # ищем конец предложения
            if end_pos != -1: 
                result = text[start_pos+len(word)+1:end_pos].strip() # вытягиваем показател который выдала модель
                if result in obj[word]: # в случае если показатель написан в точности как в объекте
                    obj[word][result]+=1    
                else:                   # в случае если показатель видоизменён
                    for key in obj[word]:
                        if key in result:
                            obj[word][key]+=1
    file.close()

print(obj)