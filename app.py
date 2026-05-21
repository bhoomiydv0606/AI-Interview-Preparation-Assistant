
from flask import Flask, render_template, request

app = Flask(__name__)

questions = [
    "Tell me about yourself",
    "What are your strengths?",
    "Why should we hire you?"
]

@app.route("/", methods=["GET", "POST"])
def home():
    feedback = ""

    if request.method == "POST":
        answer = request.form["answer"]

        if len(answer) < 30:
            feedback = "Your answer is too short."
        else:
            feedback = "Good answer. Try adding more technical details."

    return render_template("index.html", questions=questions, feedback=feedback)

if __name__ == "__main__":
    app.run(debug=True)