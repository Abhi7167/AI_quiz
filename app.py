from flask import Flask, render_template, request, redirect, session
import random
from difflib import SequenceMatcher
from questions import questions

app = Flask(__name__)
app.secret_key = "quiz_secret"

# AI similarity checking
def check_answer(user, correct):
    similarity = SequenceMatcher(None, user.lower(), correct.lower()).ratio()
    return similarity > 0.7

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    difficulty = request.form['difficulty']

    filtered = [q for q in questions if q['difficulty'] == difficulty]

    random.shuffle(filtered)

    session['questions'] = filtered[:5]
    session['score'] = 0
    session['current'] = 0

    return redirect('/quiz')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    questions_data = session['questions']
    current = session['current']

    if request.method == 'POST':
        user_answer = request.form['answer']
        correct_answer = questions_data[current]['answer']

        if check_answer(user_answer, correct_answer):
            session['score'] += 1

        session['current'] += 1
        current = session['current']

    if current >= len(questions_data):
        return redirect('/result')

    return render_template(
        'quiz.html',
        question=questions_data[current],
        qno=current + 1
    )

@app.route('/result')
def result():
    score = session['score']

    if score == 5:
        rank = "Excellent"
    elif score >= 3:
        rank = "Good"
    else:
        rank = "Beginner"

    with open("scores.txt", "a") as f:
        f.write(f"Score: {score}/5\n")

    return render_template('result.html', score=score, rank=rank)

if __name__ == '__main__':
    app.run(debug=True)