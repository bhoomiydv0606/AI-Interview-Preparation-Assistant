

from flask import Flask, render_template, request

app = Flask(__name__)

categories = {
    "HR / Behavioral": [
        "Tell me about yourself.",
        "What are your greatest strengths?",
        "What is your biggest weakness?",
        "Why should we hire you?",
        "Where do you see yourself in 5 years?",
        "Why do you want to work here?",
        "Tell me about a challenge you overcame.",
        "How do you handle stress and pressure?",
        "What motivates you?",
        "Describe your ideal work environment."
    ],
    "Technical / Coding": [
        "Explain the difference between a list and a tuple in Python.",
        "What is Object-Oriented Programming?",
        "What is the difference between SQL and NoSQL?",
        "Explain what an API is and how it works.",
        "What is version control and why is it important?",
        "What is the difference between frontend and backend development?",
        "Explain what a database index is.",
        "What is recursion? Give an example.",
        "What is the difference between HTTP and HTTPS?",
        "Explain what cloud computing is."
    ],
    "Leadership": [
        "Describe a time you led a team.",
        "How do you handle conflict within a team?",
        "Tell me about a time you motivated others.",
        "How do you prioritize tasks for your team?",
        "Describe a time you made a tough decision as a leader.",
        "How do you handle an underperforming team member?",
        "What is your leadership style?",
        "Tell me about a time you took initiative.",
        "How do you give constructive feedback?",
        "Describe a time you managed a project from start to finish."
    ],
    "Situational": [
        "What would you do if you disagreed with your manager?",
        "How would you handle a tight deadline with too much work?",
        "What would you do if a colleague was not pulling their weight?",
        "How would you handle an unhappy customer?",
        "What would you do if you made a mistake at work?",
        "How would you handle working with someone you dislike?",
        "What would you do if you were given unclear instructions?",
        "How would you handle two urgent tasks at the same time?",
        "What would you do if you saw a colleague acting unethically?",
        "How would you adapt if your role suddenly changed?"
    ],
    "Aptitude": [
        "If a train travels 60 km/h for 2.5 hours, how far does it travel?",
        "What comes next in the series: 2, 6, 12, 20, 30, ?",
        "A product costs $80 after a 20% discount. What was the original price?",
        "If 8 workers finish a job in 6 days, how many days for 12 workers?",
        "What is 15% of 240?",
        "Find the odd one out: Apple, Mango, Carrot, Banana.",
        "A clock shows 3:15. What is the angle between the hands?",
        "If A is taller than B, and B is taller than C, who is shortest?",
        "A car depreciates 10% yearly. What is its value after 2 years if it costs $10,000?",
        "Complete the analogy: Book is to Reading as Fork is to ?"
    ]
}

@app.route("/", methods=["GET", "POST"])
def home():
    feedback = ""
    selected_category = request.form.get("category", "HR / Behavioral")
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

    return render_template(
        "index.html",
        categories=categories,
        selected_category=selected_category,
        questions=categories[selected_category],
        feedback=feedback,
        answer=answer
    )

if __name__ == "__main__":
    app.run(debug=True)