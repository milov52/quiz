def divide_question_file():
    with open('questions/1vs1201.txt', 'r', encoding='KOI8-R') as questions_file:
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

    quiz = {}
    for el, question in enumerate(questions):
        quiz[question] = answers[el]

    return quiz