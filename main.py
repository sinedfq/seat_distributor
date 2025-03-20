from datetime import datetime
import json

# Собираем все элементы, соответствующие категории
def getInfoByCategory(category_id, data):
    return [cursor for cursor in data if cursor['Категория'] == category_id]

# Расчёт времени
def calculateTime(start_time, finish_time):
    start = datetime.strptime(start_time, "%H:%M:%S")
    finish = datetime.strptime(finish_time, "%H:%M:%S")
    duration = abs(finish - start)
    total_seconds = int(duration.total_seconds())
    
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{hours:02}:{minutes:02}:{seconds:02}" 

# Функция для чтения призов из текстового файла
def loadPrizes(file_path):
    prizes = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()  
            if not line: 
                continue
            parts = line.split(maxsplit=2) 
            if len(parts) >= 3: 
                try:
                    place = int(parts[0])  
                    prize = parts[2].strip()  
                    prizes[place] = prize  
                except (ValueError, IndexError):
                    continue
    return prizes

def checkAward(participants, category_id):
    # Загружаем призы из текстового файла
    match category_id:
        case "M15":
            prizes = loadPrizes('./data/prizes_list_m15.txt')
        case "M16":
            prizes = loadPrizes('./data/prizes_list_m16.txt')
        case "M18":
            prizes = loadPrizes('./data/prizes_list_m18.txt')
        case "W15":
            prizes = loadPrizes('./data/prizes_list_w15.txt')
        case "W16":
            prizes = loadPrizes('./data/prizes_list_w16.txt')
        case "W18":
            prizes = loadPrizes('./data/prizes_list_w18.txt')
    
    # Заполняем призы для участников
    for i, participant in enumerate(participants):
        place = i + 1 
        if place <= 49: 
            participant["Приз"] = prizes.get(place, "Участник не получил приз") 

# Создание и заполнение файлов
def fillJson(category_id, data):
    output_directory = './data/'
    file_path = f'{output_directory}{category_id}.json'
    
    category_data = getInfoByCategory(category_id, data)
    
    # Заполняем участников с расчетом времени
    structured_data = {
        "Категория": category_id,
        "Участники": [
            {
                "Нагрудный номер": item["Нагрудный номер"],
                "Имя Фамилия": f"{item['Имя']} {item['Фамилия']}",
                "Время": calculateTime(item["Время старта"], item["Время финиша"])
            } 
            for item in category_data
        ]
    }
    
    # Сортируем участников по времени
    structured_data["Участники"].sort(key=lambda x: (x["Время"], x["Нагрудный номер"]))

    for i, participant in enumerate(structured_data["Участники"]):
        participant["Место"] = i + 1

    checkAward(structured_data["Участники"], category_id)
    # Добавляем место для каждого участника
  
    
    # Записываем данные в файл
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(structured_data, json_file, ensure_ascii=False, indent=4)

# Основная функция
def main():
    with open('./data/race_data.json', encoding='utf-8') as f:
        data = json.load(f)

    numbers = set(item['Категория'] for item in data)

    # Заполняем файлы данными для каждой категории
    for category in numbers:
        fillJson(category, data)

if __name__ == "__main__":
    main()
