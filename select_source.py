import re, tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image

selected_file_path = filename = None
label = None

def select_source():
    def on_button_click():
        global selected_file_path, filename
        filetypes = (('.htm files', '*.htm'), ('All files', '*.*'),)

        filename = filedialog.askopenfilename(title='Select an .htm file to process', filetypes=filetypes)

        selected_file = filename
        if selected_file:
            label.config(text=f"Selected: {selected_file}",fg="green")
            button2.config(state=tk.NORMAL)
        else:
            label.config(text="No file selected",fg="red")

    global label
    root = tk.Tk()
    root.title('File Explorer')
    root.geometry("506x366")
    root.config(background="#00616b")
    root.resizable(False, False)

    popupImage = Image.open("output/semkewindow.png")
    placeImage = ImageTk.PhotoImage(popupImage)
    popupImage = tk.Label(image=placeImage)
    popupImage.place(x=2,y=2)

    button = tk.Button(root, text="Select .html File to Process", command=on_button_click,
                       activebackground="white", activeforeground="#00616b",
                       bg="#00616b", cursor="hand2", fg="white", font=("verdana", 10),
                       height=2, width=25, highlightthickness=2,overrelief="raised")
    button.place(x=50, y=235)

    button2 = tk.Button(root, text="Process Selected File", command=root.destroy,
                        activebackground="white", activeforeground="#00616b",
                        bg="#00616b", cursor="hand2", fg="white", font=("verdana", 10),
                        height=2, highlightthickness=2, overrelief="raised", state=tk.DISABLED)
    button2.place(x=300, y=235)

    label = tk.Label(root, text="No file selected",fg="red",wraplength=500,font=("verdana", 11))
    label.place(x=5, y=310)

    root.mainloop()

    source_file = open(filename, "r")
    source_data = source_file.read()

    vin_find = 0
    for i in range(0, 5):
        vin_find = source_data.find("infovalue", vin_find + 1)
    vin = source_data[vin_find+12:vin_find+29]

    start = source_data.find("<TD CLASS=\"dataheader\" WIDTH=50%>Raw Data 2</TD>")
    end = source_data[start:].find("</TABLE>")

    source_data = source_data[start+43:start+end]

    source_data = re.sub(r"<.*?>", "", source_data).replace("\n", "").replace(" ","")

    return(vin,source_data)