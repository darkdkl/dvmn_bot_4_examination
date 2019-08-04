import re
import random


def prepare_answer(answer):
    match_obj=re.search(r"^(\w|\s)+\b",answer.replace('"',''))
    return match_obj.group(0)

def filter(text):
    return re.split(r":",text.replace('\n',''),1)

def prepare_tests():

    questions_and_answers={}
    with open('./quiz-questions/1vs1201.txt','r', encoding="koi8-r") as data:
        text=data.read()
        
        for string in text.split('\n\n'):
            if 'Вопрос ' in string:
                question=filter(string)[1]
                questions_and_answers[question]=None
            elif 'Ответ:\n' in string:
                answer= filter(string)[1]
                questions_and_answers[question]=answer
         
    return random.sample( questions_and_answers.items(),1)

if __name__ == "__main__":
    prepare_tests()