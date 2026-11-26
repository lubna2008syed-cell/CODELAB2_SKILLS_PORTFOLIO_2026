import os
import random
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox

# pillow
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# colours
BG = "#EAE2F4"
PURPLE = "#796391"
TEXT = "#49385E"
WHITE = "#FFFFFF"

score = 0
questionNumber = 0
attempt = 1
difficulty = 1
correctAnswer = 0

window = tk.Tk()
window.title("Maths Quiz")
window.geometry("500x480")
window.minsize(440, 440)
window.resizable(True, True)
window.configure(bg=BG)

container = tk.Frame(window, bg=BG)
container.pack(side="top", fill="both", expand=True)

# switch between frames
def switch_to_frame(frame):
    frame.tkraise()

# make a full window page with an centred inner area of a fixed size
def createPage(colour, width=420, height=390):
    page = tk.Frame(container, bg=colour)
    page.place(x=0, y=0, relwidth=1, relheight=1)
    inner = tk.Frame(page, bg=colour)
    inner.place(relx=0.5, rely=0.5, anchor="center", width=width, height=height)
    return page, inner

# generate random numbers
def randomInt(level):
    if level == 1:
        return random.randint(1, 9)
    elif level == 2:
        return random.randint(10, 99)
    else:
        return random.randint(1000, 9999)

# choose addition or subtraction
def decideOperation():
    return random.choice(["+", "-"])

# create the quiz frames
def createQuizFrame(colour):
    frame, inner = createPage(colour)

    title = tk.Label(inner, text="", font=("Arial", 12), bg=colour, fg=TEXT)
    title.place(x=100, y=30, width=220)

    scoreText = tk.Label(inner, text="", bg=colour, fg=TEXT)
    scoreText.place(x=140, y=65, width=140)

    question = tk.Label(inner, text="", font=("Arial", 24, "bold"),
                        bg=colour, fg=TEXT)
    question.place(x=60, y=115, width=300, height=50)

    entry = tk.Entry(inner, font=("Arial", 14), justify="center")
    entry.place(x=130, y=190, width=160, height=35)

    attempts = tk.Label(inner, text="", bg=colour, fg=TEXT)
    attempts.place(x=120, y=235, width=180)

    tk.Button(inner, text="Submit Answer", bg=PURPLE, fg=WHITE,
              command=lambda: submitAnswer()).place(x=130, y=275, width=160, height=40)

    # quit mid test and go back to the menu
    tk.Button(inner, text="Quit to Menu", bg="#B5565B", fg=WHITE,
              command=lambda: quitToMenu()).place(x=130, y=325, width=160, height=35)

    entry.bind("<Return>", lambda event: submitAnswer())

    return frame, (title, scoreText, question, entry, attempts)

# quit the current quiz and choose another mode
def quitToMenu():
    if messagebox.askyesno("Quit Quiz", "Quit this quiz and go back to the menu?\nYour progress will be lost."):
        switch_to_frame(menuFrame)

# display a question
def displayProblem():
    global questionNumber, attempt, correctAnswer

    questionNumber += 1
    attempt = 1

    num1 = randomInt(difficulty)
    num2 = randomInt(difficulty)
    operation = decideOperation()

    if operation == "+":
        correctAnswer = num1 + num2
    else:
        correctAnswer = num1 - num2

    currentWidgets[0].config(text=f"Question {questionNumber} of 10")
    currentWidgets[1].config(text=f"Score: {score}")
    currentWidgets[2].config(text=f"{num1} {operation} {num2} = ?")
    currentWidgets[3].delete(0, tk.END)
    currentWidgets[4].config(text="Attempt 1 of 2")

    currentWidgets[3].focus()
    switch_to_frame(currentFrame)

# check the answer
def isCorrect(answer):
    if answer == correctAnswer:
        if attempt == 1:
            messagebox.showinfo("Correct", "You earned 10 points!")
        else:
            messagebox.showinfo("Correct", "You earned 5 points!")
        return True

    elif attempt == 1:
        messagebox.showwarning("Wrong", "Try one more time!")
    else:
        messagebox.showerror("Wrong", f"The correct answer was {correctAnswer}")

    return False

# submit answer
def submitAnswer():
    global score, attempt

    try:
        answer = int(currentWidgets[3].get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Enter a whole number.")
        currentWidgets[3].delete(0, tk.END)
        currentWidgets[3].focus()
        return

    if isCorrect(answer):
        score += 10 if attempt == 1 else 5
        nextQuestion()

    elif attempt == 1:
        attempt = 2
        currentWidgets[4].config(text="Attempt 2 of 2")
        currentWidgets[3].delete(0, tk.END)
        currentWidgets[3].focus()

    else:
        nextQuestion()

# move to the next question
def nextQuestion():
    if questionNumber < 10:
        displayProblem()
    else:
        displayResults()

# display final score and grade
def displayResults():
    if score > 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 60:
        grade = "C"
    elif score >= 50:
        grade = "D"
    else:
        grade = "F"

    resultScore.config(text=f"Final Score: {score}/100")
    gradeLabel.config(text=f"Grade: {grade}")

    switch_to_frame(resultFrame)

# start the quiz
def startQuiz(level):
    global score, questionNumber, difficulty
    global currentFrame, currentWidgets

    score = 0
    questionNumber = 0
    difficulty = level

    currentFrame, currentWidgets = quizFrames[level]
    displayProblem()

# menu frame

menuFrame = tk.Frame(container, bg=BG)
menuFrame.place(x=0, y=0, relwidth=1, relheight=1)

bgLabel = tk.Label(menuFrame, bg=BG)
bgLabel.place(x=0, y=0, relwidth=1, relheight=1)

imagePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz.png")
originalImage = None
bgPhoto = None

try:
    if HAS_PIL:
        originalImage = Image.open(imagePath)
    else:
        bgPhoto = tk.PhotoImage(file=imagePath)     # fixed size without Pillow
        bgLabel.config(image=bgPhoto)
except Exception:
    print("Could not load quiz.png - make sure it is in the same folder as this file.")

def resizeBackground(event):
    global bgPhoto
    if originalImage is not None and event.width > 1 and event.height > 1:
        resized = originalImage.resize((event.width, event.height))
        bgPhoto = ImageTk.PhotoImage(resized)
        bgLabel.config(image=bgPhoto)

menuFrame.bind("<Configure>", resizeBackground)

# scaling list
scalables = []

def registerScalable(inner, baseW, baseH):
    items = []
    for widget in inner.winfo_children():
        info = widget.place_info()
        f = tkfont.Font(font=widget.cget("font"))
        height = int(info["height"]) if info.get("height") else None
        items.append((widget, int(info["x"]), int(info["y"]), int(info["width"]),
                      height, f.actual("family"), abs(f.actual("size")), f.actual("weight")))
    scalables.append((inner, baseW, baseH, items))

def rescale(event=None):
    s = max(1, min(container.winfo_width() / 420, container.winfo_height() / 390))

    for inner, baseW, baseH, items in scalables:
        inner.place(width=int(baseW * s), height=int(baseH * s))
        for widget, x, y, w, h, family, size, weight in items:
            options = dict(x=int(x * s), y=int(y * s), width=int(w * s))
            if h:
                options["height"] = int(h * s)
            widget.place(**options)
            widget.config(font=(family, max(1, round(size * s)), weight))

# Display the difficulty menu
def displayMenu():
    card = tk.Frame(menuFrame, bg=BG)
    card.place(relx=0.5, rely=0.5, anchor="center", width=300, height=290)

    tk.Label(card, text="Maths Quiz", font=("Arial", 22, "bold"),
             bg=BG, fg=TEXT).place(x=40, y=20, width=220, height=45)

    tk.Label(card, text="Choose your difficulty", font=("Arial", 13),
             bg=BG, fg=TEXT).place(x=30, y=75, width=240, height=30)

    tk.Button(card, text="Easy", bg="#9DBB99", fg=WHITE,
              command=lambda: startQuiz(1)).place(x=70, y=120, width=160, height=40)

    tk.Button(card, text="Moderate", bg="#83A9D5", fg=WHITE,
              command=lambda: startQuiz(2)).place(x=70, y=175, width=160, height=40)

    tk.Button(card, text="Advanced", bg="#C68CA7", fg=WHITE,
              command=lambda: startQuiz(3)).place(x=70, y=230, width=160, height=40)

    # Register card for scaling inside the function where card exists
    registerScalable(card, 300, 290)

displayMenu()

# quiz frames

quizFrames = {}

quizFrames[1] = createQuizFrame("#DDEBD9")  # Easy - green
quizFrames[2] = createQuizFrame("#DCE8F6")  # Moderate - blue
quizFrames[3] = createQuizFrame("#F3DFE7")  # Advanced - pink

# results frame 

resultFrame, resultInner = createPage(BG)

tk.Label(resultInner, text="Quiz Completed!", font=("Arial", 22, "bold"),
         bg=BG, fg=TEXT).place(x=90, y=55, width=240, height=45)

resultScore = tk.Label(resultInner, text="", font=("Arial", 15),
                       bg=BG, fg=TEXT)
resultScore.place(x=70, y=135, width=280, height=35)

gradeLabel = tk.Label(resultInner, text="", font=("Arial", 18, "bold"),
                      bg=BG, fg=TEXT)
gradeLabel.place(x=100, y=180, width=220, height=40)

tk.Button(resultInner, text="Play Again", bg=PURPLE, fg=WHITE,
          command=lambda: switch_to_frame(menuFrame)).place(x=130, y=245, width=160, height=40)

tk.Button(resultInner, text="Quit", bg=PURPLE, fg=WHITE,
          command=window.destroy).place(x=130, y=295, width=160, height=40)

# Register quiz and result frames for scaling
for level in quizFrames:
    registerScalable(quizFrames[level][0].winfo_children()[0], 420, 390)
registerScalable(resultInner, 420, 390)

container.bind("<Configure>", rescale)

# display the menu first
switch_to_frame(menuFrame)

window.mainloop()
