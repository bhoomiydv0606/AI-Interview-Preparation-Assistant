

from flask import Flask, render_template, request

app = Flask(__name__)

categories = {
    "HR / Behavioral": {
        "Easy": [
            "Tell me about yourself.",
            "What are your hobbies?",
            "Why do you want this job?",
        ],
        "Medium": [
            "What is your greatest strength?",
            "What is your biggest weakness?",
            "Where do you see yourself in 5 years?",
            "How do you handle stress and pressure?",
        ],
        "Hard": [
            "Tell me about a conflict you had with a colleague and how you resolved it.",
            "Describe a time you failed and what you learned from it.",
            "Give an example of a time you showed leadership under pressure.",
        ]
    },
    "Technical / Coding": {
        "Easy": [
            "What is the difference between frontend and backend?",
            "What is an API?",
            "What is version control?",
        ],
        "Medium": [
            "Explain Object-Oriented Programming with an example.",
            "What is the difference between SQL and NoSQL?",
            "What is recursion? Give a real-world example.",
            "Explain what a REST API is.",
        ],
        "Hard": [
            "How would you optimize a slow database query?",
            "Explain the difference between concurrency and parallelism.",
            "How does a hash map work internally?",
        ]
    },
    "Leadership": {
        "Easy": [
            "Have you ever led a group project?",
            "How do you organize your own work?",
            "What does good teamwork mean to you?",
        ],
        "Medium": [
            "Describe a time you motivated a team member.",
            "How do you handle conflict within a team?",
            "How do you prioritize tasks for your team?",
            "What is your leadership style?",
        ],
        "Hard": [
            "Describe a time you had to make a tough decision that affected your whole team.",
            "Tell me about a time you led a failing project back to success.",
            "How would you handle a senior team member who refuses to follow your direction?",
        ]
    },
    "Situational": {
        "Easy": [
            "What would you do if you didn't understand a task given to you?",
            "How would you ask for help if you were stuck?",
            "What would you do if you were going to miss a deadline?",
        ],
        "Medium": [
            "What would you do if you disagreed with your manager's decision?",
            "How would you handle working with someone you dislike?",
            "What would you do if two urgent tasks arrived at the same time?",
            "How would you handle an unhappy customer?",
        ],
        "Hard": [
            "What would you do if you discovered a colleague was acting unethically?",
            "How would you handle a situation where your team is demotivated and behind schedule?",
            "What would you do if you were asked to do something that goes against company policy?",
        ]
    },
    "Aptitude": {
        "Easy": [
            "What comes next in the series: 2, 4, 8, 16, ?",
            "Find the odd one out: Apple, Mango, Carrot, Banana.",
            "If A is taller than B and B is taller than C, who is the shortest?",
        ],
        "Medium": [
            "A train travels 60 km/h for 2.5 hours. How far does it travel?",
            "A product costs $80 after a 20% discount. What was the original price?",
            "What is 15% of 240?",
            "If 8 workers finish a job in 6 days, how many days for 12 workers?",
        ],
        "Hard": [
            "A clock shows 3:15. What is the angle between the hour and minute hands?",
            "A car depreciates 10% per year. What is its value after 2 years if it originally costs $10,000?",
            "Complete the analogy: Book is to Reading as Fork is to ?",
        ]
    }
}

@app.route("/", methods=["GET", "POST"])
def home():
    feedback = ""
    selected_category = request.form.get("category", "HR / Behavioral")
    selected_difficulty = request.form.get("difficulty", "Easy")
    answer = request.form.get("answer", "")

    if request.method == "POST" and answer:
        if len(answer) < 30:
            feedback = "Your answer is too short. Try to elaborate with specific examples."
        elif len(answer) < 80:
            feedback = "Decent answer! Add more detail and real examples to strengthen it."
        elif len(answer) < 150:
            feedback = "Good answer! Try adding measurable outcomes or specific results."
        else:
            feedback = "Excellent answer! Well-detailed and structured response."

    questions = categories[selected_category][selected_difficulty]

    return render_template(
        "index.html",
        categories=categories,
        selected_category=selected_category,
        selected_difficulty=selected_difficulty,
        questions=questions,
        feedback=feedback,
        answer=answer
    )

if __name__ == "__main__":
    app.run(debug=True)