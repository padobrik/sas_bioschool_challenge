import pandas as pd
import numpy as np


# Определим необходимые функции для работы с данными

# Считаем уникальные идентификаторы посещений
def unique_counter(data):
    visits_unique = list(data.VISITN.drop_duplicates())
    for i in range(len(visits_unique) - 1):
        if int(visits_unique[i + 1]) - int(visits_unique[i]) > 1:
            visits_unique.remove(visits_unique[i + 1]) # Избегаем неопределенных визитов, в датасете они выглядят как '99'/'Undefined'
    visits_unique.sort()

    return visits_unique

# Вытаскиваем исследуемую величину для каждой группы и удаляем пустые величины
def visit_avals(visit_n, group, data):
    group_num = group.replace('group_n_', '')
    treatment_data = data.loc[data.TRTGRPN == str(group_num)]
    avals = list(treatment_data.loc[treatment_data.VISITN == visit_n].AVAL.astype(float))
    avals = [i for i in avals if str(i) != 'nan']
    
    return avals

# С этой функцией делаем расчет требуемых статистических параметров

def stats(item):
    stats_l = []
    n = np.round_(len(item[0]), decimals=0)
    mean = np.round_(np.mean(item[0]), decimals=1)
    std = np.round_(np.std(item[0]), decimals=2)
    minimum = int(np.min(item[0]))
    maximum = int(np.max(item[0]))
    stats_l.extend([str(n), 
                    str(mean), 
                    str(std), 
                    str(minimum), 
                    str(maximum)])
    item.append(stats_l)

# Будем формировать по каждому визиту отдельный датасет, а затем подключать его к нашей цепочке данных
def visit_dataframe(visit_number, visit_stats, main_df):
    if visit_number >= 10:
        name = 'Visit ' + str(visit_number)
    else:
        name = 'Visit 0' + str(visit_number)
    tr_g1 = 'Treatment Group 1 (N=' + str(len(main_df.loc[main_df.TRTGRPN == '1'])) + ')'
    tr_g2 = 'Treatment Group 2 (N=' + str(len(main_df.loc[main_df.TRTGRPN == '2'])) + ')'
    column_names = ['Visit', tr_g1, tr_g2]
    visit_1 = pd.DataFrame(columns = column_names)
    visit_1 = visit_1.append({'Visit': name}, ignore_index=True)

    parameters = [' n', 
                ' Mean', 
                ' Standart Deviation', 
                ' Minimum', 
                ' Maximum']
    visit_2 = pd.DataFrame(columns = column_names)
    visit_2.iloc[:, 0] = parameters
    visit_2.iloc[:, 1] = visit_stats[0]
    visit_2.iloc[:, 2] = visit_stats[1]

    visit_list = [visit_1]
    visit_list.append(visit_2)
    visit = pd.concat(visit_list)
    visit.loc[visit.shape[0]] = [' ', ' ', ' ']
    
    return visit

# Открываем датафрейм с помощью библиотеки pandas:
df = pd.read_csv('dataset.csv', sep=';')
main = df.loc[df.PARAMCD == 'EFF01'][1:] # Нас интересует Efficacy Parameter 1

# Создаем датафрейм с результатами обработки, это позволит вносить изменения в случае корректировок       
tr_g1 = 'Treatment Group 1 (N=' + str(len(main.loc[main.TRTGRPN == '1'])) + ')'
tr_g2 = 'Treatment Group 2 (N=' + str(len(main.loc[main.TRTGRPN == '2'])) + ')'
column_names = ['Visit', tr_g1, tr_g2]
out_1 = pd.DataFrame(columns = column_names)
out = out_1.append({'Visit': ' Statistics'}, ignore_index=True)

# Определим словарь для статистических параметров:
params = {}
group_nums = ['group_n_' + str(k) for k in range(1, len(list(main.TRTGRPN.drop_duplicates())) + 1)]
visit_nums = ['visit_n_' + str(visit_num) for visit_num in unique_counter(main)]
for i in range(len(group_nums)):
    params[group_nums[i]] = {visit_num: [visit_avals(n, group_nums[i], main)] for visit_num, n in zip(visit_nums, unique_counter(main))}

# Получаем требуемые статистические параметры:
for group, visits in params.items():
    for visit, item in visits.items():
        stats(item)

# Вносим их в нашу таблицу:
out_list = [out]
for i in range(1, len(unique_counter(main)) + 1):
    visit_stats = []
    for group, visits in params.items():
        visit_stats.append(visits['visit_n_' + str(i)][1])
    out_list.append(visit_dataframe(i, visit_stats, main))
final_out = pd.concat(out_list)
final_out = final_out.append({'Visit': 'N: Number of subjects in the population and treatment group.'}, ignore_index=True)

# Сохраняем промежуточный .txt файл
final_out.to_csv('out.txt', sep=',', index=False)

# Открываем полученный аутпут в режиме чтения для переноса содержания в конечный файл

with open('out.txt', "r") as f:
    data = f.readlines()
    new_data = []
    for item in data:
        new_data.extend([[item]])

# Для решения проблемы красивого заполнения данных в .txt файле создаем двумерный массив с пробелами. Вставлять требуемые величины будем
# по координатам матрицы

# Однако не считаю предложенные форматы файлов (.txt, .doc, .pdf) правильными для построения результатов анализа. С этой задачей прекрасно
# справляется, например, .csv :)

matrix = [[' ' for i in range(105)] for j in range(len(new_data))]

array = []
for line in new_data:
    for item in line:
        word = item.replace('\n', '').split(',')
        array.append(word)

# Определяем функцию которая будет записывать данные с датасета в результирующий файл

def builder(item, matrix, x, y):
    for i in range(len(item)):
        matrix[y][x + i] = item[i]

line_x = [0, 32, 73] # Координата начала вставки интересующей ячейки
for j in range(len(array)):
    line = array[j]
    for i in range(len(line)):
        builder(line[i], matrix, line_x[i], j)

# Записываем результирующий файл и дополняем необходимыми элементами

with open('result.txt', 'w') as file:
    file.write('Table: Summary of Efficacy Parameter 1 by Visit. Intention-to-Treat population \n')
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            file.write(matrix[i][j])
        file.write('\n')