import re
from pprint import pprint


def main():
    with open('questions/1vs1200.txt', 'r', encoding='KOI8-R') as questions_file:
        file_data = questions_file.read().split('\n\n')

    questions = []
    answers = []
    for data in file_data:
        if data.startswith('Вопрос') or data.startswith('\nВопрос'):
            data = data.replace('\n', ' ')
            questions.append(data[data.find(':')+2:])

        if data.startswith('Ответ') or data.startswith('\nОтвет'):
            data = data.replace('\n', ' ')
            answers.append(data[data.find(':')+2:])

    print(questions)
    print(answers)


if __name__ == '__main__':
    main()
