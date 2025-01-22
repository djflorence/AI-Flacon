import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from PIL import Image, ImageTk  # For images
import json
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load the model and tokenizer
model_name = "tiiuae/falcon-7b-instruct"
print("Loading Falcon model...")
tokenizer = AutoTokenizer.from_pretrained(
    model_name
)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype="auto"
)
print("Model loaded successfully!")

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

# Clear responses
def clear_responses():
    response_text.delete(1.0, tk.END)
    short_term_memory.clear()

# Generate a response
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
    else:
        try:
            context = "\n".join(short_term_memory[-5:])
            inputs = tokenizer(context, return_tensors="pt").to("cuda")
            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                num_beams=3,
                no_repeat_ngram_size=2,
                temperature=0.7,
                early_stopping=True
            )
            response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        except Exception as e:
            response = f"An error occurred while generating the response: {e}"

    short_term_memory.append(f"A: {response}")
    response_text.insert(tk.END, f"Q: {user_input}\nA: {response}\n\n")

# Initialize the Tkinter window
window = tk.Tk()
window.title("Enhanced Falcon Chat - Customizable")
window.geometry("800x600")

# Background Image
bg_image = Image.open("C:/ai/images/background.jpg")  # Replace with your image path
bg_image = bg_image.resize((800, 600), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(window, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# Styled Widgets
title_label = tk.Label(window, text="Welcome to Falcon Chat", font=("Arial", 24, "bold"), bg="black", fg="white")
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
