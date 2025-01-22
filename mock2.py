import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence  # For images
import json
import requests  # For internet access

# Mock Model Loading
print("Model loading skipped for testing.")

# Memory storage
short_term_memory = []
long_term_memory_file = "long_term_memory.json"

# Load long-term memory
try:
    with open(long_term_memory_file, "r") as f:
        long_term_memory = json.load(f)
except FileNotFoundError:
    long_term_memory = {}

# Save long-term memory
def save_long_term_memory():
    with open(long_term_memory_file, "w") as f:
        json.dump(long_term_memory, f)

# Function to handle arithmetic questions
def handle_math(question):
    try:
        sanitized_question = question.replace(" ", "")
        result = eval(sanitized_question, {"__builtins__": None}, {})
        return f"The answer is {result}."
    except Exception as e:
        return f"Sorry, I couldn't evaluate the question. Error: {e}"

# Function to handle web queries
def handle_web_query(query):
    try:
        search_url = f"https://www.google.com/search?q={query}"
        response = requests.get(search_url)
        if response.status_code == 200:
            return f"Here is a link to the search results: {search_url}"
        else:
            return "Failed to fetch search results. Please try again."
    except Exception as e:
        return f"Error while performing the search: {e}"

# Clear responses
def clear_responses():
    response_text.delete(1.0, tk.END)
    short_term_memory.clear()

# Generate a response (Mock Implementation)
def generate_response():
    global short_term_memory
    user_input = question_entry.get()
    if not user_input.strip():
        response_text.insert(tk.END, "Please enter a question.\n")
        return

    short_term_memory.append(f"Q: {user_input}")
    short_term_memory = short_term_memory[-5:]

    if any(op in user_input for op in "+-*/"):
        response = handle_math(user_input)
    elif user_input.lower().startswith("search"):
        query = user_input[7:].strip()  # Extract query after "search"
        response = handle_web_query(query)
    else:
        response = f"Mock response for: {user_input}"

    short_term_memory.append(f"A: {response}")
    response_text.insert(tk.END, f"Q: {user_input}\nA: {response}\n\n")

# Initialize the Tkinter window
window = tk.Tk()
window.title("Enhanced Falcon Chat - Customizable")
window.geometry("800x600")

# Background Image
bg_image = Image.open("c:/ai/images/background.jpg")  # Replace with your image
bg_image = bg_image.resize((800, 600), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(window, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# Animated Avatar Class
class AnimatedGIF(tk.Label):
    def __init__(self, master, gif_path, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.gif = Image.open(gif_path)
        self.frames = [ImageTk.PhotoImage(frame.copy().convert('RGBA')) for frame in ImageSequence.Iterator(self.gif)]
        self.frame_index = 0
        self.update_animation()

    def update_animation(self):
        self.config(image=self.frames[self.frame_index])
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.after(100, self.update_animation)  # Adjust the delay as needed

# Add the animated avatar
avatar = AnimatedGIF(window, "c:/ai/images/Main.gif")
avatar.pack(side=tk.LEFT, padx=10, pady=10)

# Styled Widgets
title_label = tk.Label(window, text="Welcome to Our Chat", font=("Arial", 24, "bold"), bg="black", fg="white")
title_label.pack(pady=10)

question_label = tk.Label(window, text="Enter your question:", font=("Arial", 14), bg="black", fg="white")
question_label.pack(pady=5)

question_entry = ttk.Entry(window, width=60, font=("Arial", 14))
question_entry.pack(pady=5)

submit_button = ttk.Button(window, text="Ask Falcon", command=generate_response)
submit_button.pack(pady=5)

clear_button = ttk.Button(window, text="Clear", command=clear_responses)
clear_button.pack(pady=5)

response_text = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=20, font=("Courier", 12))
response_text.pack(pady=10)

# Start the Tkinter event loop
window.mainloop()
