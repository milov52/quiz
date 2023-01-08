import os, glob

def divide_question_file():
    quiz = {}
    questions = []
    answers = []

    path = './questions/'
    for filename in glob.glob(os.path.join(path, '*.txt')):
        with open(os.path.join(os.getcwd(), filename), 'r', encoding='KOI8-R') as questions_file:
            file_data = questions_file.read().split('\n\n')


        for data in file_data:
            if data.startswith('Вопрос') or data.startswith('\nВопрос'):
                data = data.replace('\n', ' ')
                questions.append(data[data.find(':')+2:])

            if data.startswith('Ответ') or data.startswith('\nОтвет'):
                data = data.replace('\n', ' ')
                answers.append(data[data.find(':')+2:])

        for el, question in enumerate(questions):
            quiz[question] = answers[el]

    return quiz
