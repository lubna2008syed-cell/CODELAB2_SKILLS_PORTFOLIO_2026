import os
import random
import tkinter as tk
import tkinter.font as tkfont

# pillow
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# colours
BG = "#DCEEFF"
BOX = "#F0F7FF"
BLUE = "#4A90D9"
DARK_BLUE = "#234F80"

# load the jokes
jokes = []

scriptFolder = os.path.dirname(os.path.abspath(__file__))
filePath = os.path.join(scriptFolder, "randomJokes.txt")

try:
    with open(filePath, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line.startswith("-"):
                line = line[1:].strip()

            if "?" in line:
                setup, punchline = line.split("?", 1)
                jokes.append((setup + "?", punchline.strip()))
except FileNotFoundError:
    print(f"Warning: 'randomJokes.txt' not found in {scriptFolder}. Using default jokes.")
    jokes = [
        ("Why don't scientists trust atoms?", "Because they make up everything!"),
        ("What do you call a fake noodle?", "An impasta!")
    ]

history = []
position = -1

# functions
def showJoke():
    if not history or position < 0 or position >= len(history):
        return
    setup, punchline = history[position]
    setupLabel.config(text=setup)
    punchlineLabel.config(text="")
    updatePreviousButton()

def updatePreviousButton():
    previousButton.config(state="normal" if position > 0 else "disabled")

def tellJoke():
    global position

    if not jokes:
        setupLabel.config(text="No jokes found!")
        return

    joke = random.choice(jokes)

    # prevent infinite loop if all jokes in the list are identical
    attempts = 0
    if len(jokes) > 1 and history:
        while joke == history[position] and attempts < 50:
            joke = random.choice(jokes)
            attempts += 1

    history.append(joke)
    position = len(history) - 1
    showJoke()

def previousJoke():
    global position

    if position > 0:
        position -= 1
        showJoke()

def nextJoke():
    global position

    if position < len(history) - 1:
        position += 1
        showJoke()
    else:
        tellJoke()

def showPunchline():
    if history and 0 <= position < len(history):
        punchlineLabel.config(text=history[position][1])

# main window
window = tk.Tk()
window.title("Alexa Joke Assistant")
window.geometry("500x480")
window.minsize(460, 440)
window.resizable(True, True)
window.config(bg=BG)

container = tk.Frame(window, bg=BG)
container.pack(fill="both", expand=True)


# background image
bgLabel = tk.Label(container, bg=BG)
bgLabel.place(x=0, y=0, relwidth=1, relheight=1)

imagePath = os.path.join(scriptFolder, "joke.png")
originalImage = None
bgPhoto = None

try:
    if HAS_PIL and os.path.exists(imagePath):
        originalImage = Image.open(imagePath)
    elif os.path.exists(imagePath):
        bgPhoto = tk.PhotoImage(file=imagePath)
        bgLabel.config(image=bgPhoto)
except Exception:
    print("Could not load joke.png - background color will be used instead.")


def resizeBackground(event):
    global bgPhoto

    if originalImage is not None and event.width > 1 and event.height > 1:
        resized = originalImage.resize((event.width, event.height))
        bgPhoto = ImageTk.PhotoImage(resized)
        bgLabel.config(image=bgPhoto)


bgLabel.bind("<Configure>", resizeBackground)

# centered card
card = tk.Frame(container, bg=BG)
card.place(relx=0.5, rely=0.5, anchor="center", width=400, height=370)

titleLabel = tk.Label(card, text="Joke Machine", font=("Arial", 20, "bold"),
                      bg=BG, fg=DARK_BLUE)
titleLabel.place(x=40, y=10, width=320, height=40)

alexaButton = tk.Button(card, text="Alexa tell me a Joke",
                        font=("Arial", 12, "bold"), bg=BLUE, fg="white",
                        activebackground=DARK_BLUE, activeforeground="white",
                        command=tellJoke)
alexaButton.place(x=80, y=60, width=240, height=40)

setupLabel = tk.Label(card, text="Your joke will appear here!",
                      font=("Arial", 12), bg=BOX, fg=DARK_BLUE, wraplength=340,
                      highlightbackground=BLUE, highlightthickness=2)
setupLabel.place(x=20, y=115, width=360, height=80)

punchlineLabel = tk.Label(card, text="", font=("Arial", 12, "italic"),
                          bg=BOX, fg=DARK_BLUE, wraplength=340,
                          highlightbackground=BLUE, highlightthickness=2)
punchlineLabel.place(x=20, y=205, width=360, height=80)

previousButton = tk.Button(card, text="Previous Joke", font=("Arial", 10),
                           bg=BLUE, fg="white", activebackground=DARK_BLUE,
                           command=previousJoke, state="disabled")
previousButton.place(x=10, y=300, width=120, height=35)

punchlineButton = tk.Button(card, text="Show Punchline", font=("Arial", 10),
                            bg=BLUE, fg="white", activebackground=DARK_BLUE,
                            command=showPunchline)
punchlineButton.place(x=140, y=300, width=120, height=35)

nextButton = tk.Button(card, text="Next Joke", font=("Arial", 10),
                       bg=BLUE, fg="white", activebackground=DARK_BLUE,
                       command=nextJoke)
nextButton.place(x=270, y=300, width=120, height=35)

quitButton = tk.Button(card, text="Quit", font=("Arial", 10),
                       bg="#B5565B", fg="white", activebackground=DARK_BLUE,
                       command=window.destroy)
quitButton.place(x=140, y=340, width=120, height=28)

# scaling
items = []

for widget in card.winfo_children():
    info = widget.place_info()
    f = tkfont.Font(font=widget.cget("font"))

    try:
        wrap = int(widget.cget("wraplength"))
    except (tk.TclError, ValueError):
        wrap = 0

    items.append((widget, int(info["x"]), int(info["y"]),
                  int(info["width"]), int(info["height"]),
                  f.actual("family"), abs(f.actual("size")),
                  f.actual("weight"), f.actual("slant"), wrap))

def rescale(event=None):
    s = max(1, min(container.winfo_width() / 500,
                   container.winfo_height() / 440))

    card.place(width=int(400 * s), height=int(370 * s))

    for widget, x, y, w, h, family, size, weight, slant, wrap in items:
        widget.place(x=int(x * s), y=int(y * s),
                     width=int(w * s), height=int(h * s))

        widget.config(font=(family, max(1, round(size * s)), weight, slant))

        if wrap:
            widget.config(wraplength=int(wrap * s))

container.bind("<Configure>", rescale)

window.mainloop()
