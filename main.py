
def main():
    with open('questions/1vs1200.txt', 'r', encoding='KOI8-R') as questions_file:
        questions = questions_file.read()

    print(questions)

if __name__ == '__main__':
    main()