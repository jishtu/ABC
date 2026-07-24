from tkinter import *
from tkinter import ttk
from deep_translator import GoogleTranslator

# Function to translate text
def translate_text():
    text = text1.get("1.0", END).strip()

    if text:
        translated = GoogleTranslator(
            source='auto',
            target=combo2.get().lower()
        ).translate(text)

        text2.delete("1.0", END)
        text2.insert(END, translated)

# Function to swap languages
def swap_languages():
    lang1 = combo1.get()
    lang2 = combo2.get()

    combo1.set(lang2)
    combo2.set(lang1)

# Main Window
root = Tk()
root.title("Google Translator")
root.geometry("5000x5000")
root.configure(bg="blue")

# Language List
languages = [
    "English", "Hindi", "French", "German",
    "Spanish", "Japanese", "Korean",
    "Russian", "Arabic", "Chinese"
]

# Left Language Dropdown
combo1 = ttk.Combobox(root, values=languages, font=("Arial", 14))
combo1.place(x=50, y=20, width=250)
combo1.set("English")

# Right Language Dropdown
combo2 = ttk.Combobox(root, values=languages, font=("Arial", 14))
combo2.place(x=700, y=20, width=250)
combo2.set("Hindi")

# Language Labels
label1 = Label(root, text="ENGLISH",
               font=("Arial", 22, "bold"),
               bg="white")
label1.place(x=120, y=60)

label2 = Label(root, text="SELECT LANGUAGE",
               font=("Arial", 22, "bold"),
               bg="white")
label2.place(x=650, y=60)

# Left Text Box
text1 = Text(root,
             font=("Arial", 14),
             wrap=WORD,
             bd=3,
             relief=SOLID)

text1.place(x=20, y=120, width=420, height=250)

# Right Text Box
text2 = Text(root,
             font=("Arial", 14),
             wrap=WORD,
             bd=3,
             relief=SOLID)

text2.place(x=560, y=120, width=420, height=250)

# Swap Button
swap_btn = Button(root,
                  text="↔️",
                  font=("Arial", 24, "bold"),
                  command=swap_languages,
                  bg="lightblue")

swap_btn.place(x=470, y=150, width=70, height=50)

# Translate Button
translate_btn = Button(root,
                       text="Translate",
                       font=("Arial", 14, "bold"),
                       command=translate_text,
                       bg="black",
                       fg="white")

translate_btn.place(x=1000, y=250, width=100, height=50)

root.mainloop()
