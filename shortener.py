import pyshorteners
import tkinter as tk
from tkinter import  messagebox

def shorten_url():
    url=url_entry.get().strip()

    if not url:
        messagebox.showwarning("Input Error", "Please enter a valid URL.")
        return
    
    if not url.startswith(("http://","https://")):
        url= "http://" + url

        
    
    try:
        shortener = pyshorteners.Shortener()
        short_url= shortener.tinyurl.short(url)
        
        
        result_label.config(text=f"Shorten URL: {short_url}",fg="blue")
        copy_button.config(state=tk.NORMAL)
        result_label.short_url = short_url

    except Exception as e:
        messagebox.showerror("Shortening Failed", f"An error occured:\n\n{str(e)}")
        result_label.config(text="")
        copy_button.config(state=tk.DISABLED)

    

root= tk.Tk()
root.title=("URL Shortener")
root.geometry("400x250")
root.resizable(False,False)

title_label= tk.Label(root, text="Simple URL Shortener", font=("Helvetica", 14))
title_label.pack(pady=10)

url_entry= tk.Entry(root, width=50)
url_entry.pack(pady=5)

shorten_button= tk.Button(root, text="Shorten URL", command=shorten_url)
shorten_button.pack(pady=5)

def copy_to_clipboard():
        short_url=getattr(result_label, "short_url", "")
        if short_url:
            root.clipboard_clear()
            root.clipboard_append(short_url)
            messagebox.showinfo("Copied", "Shorten URL copied to clipboard!")

copy_button= tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.pack(pady=5)
copy_button.config(state=tk.DISABLED)

result_label = tk.Label(root, text="", wraplength=350, fg="blue")
result_label.pack(pady=10)


root.mainloop()
