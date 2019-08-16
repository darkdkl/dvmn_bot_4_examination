import re
import random


def prepare_answer(answer):
    match_obj=re.search(r"^(\w|\s)+\b",answer.replace('"',''))
    prepared_answer=match_obj.group(0)
    return prepared_answer.strip()

def text_filter(text):
    return re.split(r":",text.replace('\n',' '),1)

def get_random_questions_and_answers():

    return random.sample(prepare_questions_and_answers().items(), 1)



def prepare_questions_and_answers(filepath='./quiz-questions/1vs1201.txt'):

    questions_and_answers={}
    with open(filepath,'r', encoding="koi8-r") as file:
        text=file.read()
        
        for string in text.split('\n\n'):
            if 'Вопрос ' in string:
                question=text_filter(string)[1]
                questions_and_answers[question]=None
            elif 'Ответ:\n' in string:
                answer= text_filter(string)[1]
                questions_and_answers[question]=answer
         
    return questions_and_answers

if __name__ == "__main__":
    get_random_questions_and_answers()
