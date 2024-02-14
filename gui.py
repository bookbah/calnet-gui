import os
import librosa
import time
import numpy as np
import customtkinter
from customtkinter import filedialog
from datetime import datetime
import threading

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.title("CalNet Audio GUI")
root.wm_iconbitmap('assets/icons/sino-icon.ico')
root.geometry("750x500")
root.resizable(width=True, height=False)

today = datetime.today()

def calculate_net_audio(wav_file, progress_var):
    # Load the WAV file
    y, sr = librosa.load(wav_file)

    # Trim leading and trailing silence
    y_trimmed, _ = librosa.effects.trim(y)

    # Get the first 5 minutes (300 seconds)
    y_cut = y_trimmed[:int(sr * 300)]

    # Calculate the Net Audio for the selected portion
    net_audio = np.sum(np.abs(y_cut)) / np.max(np.abs(y_cut))
    progress_var.set(100) # Set progress to 100% when analysis is complete
    return net_audio

def select_wav_file():
    file_path = filedialog.askopenfilename(title='Open a .wav file', filetypes=[("WAV files", "*.wav"),("All files", "*.*")])
    file_name = os.path.splitext(os.path.basename(f'{file_path}.wav'))[0]
    # print(f'Selected full file path: {file_path}')  # Add this line for debugging
    # print(f'Selected file: {file_name}')  # Add this line for debugging
    file_name_label.configure(text=f'File name: {file_name}')
    entry_filepath.delete(0, customtkinter.END)
    entry_filepath.insert(0, file_path)
    progress_var.set(0) # reset progress to 0%
    bottom_label.configure(text="Status: Please start !")
    progress_bar.pack_forget()  # Hide the progress bar after the analysis completes
    
def analyze_file():
    file_path = entry_filepath.get()
    file_name = os.path.splitext(os.path.basename(f'{file_path}'))[0]
    print(f'analyzed file: {file_path}')
    try:        
        button_browse.configure(state="disabled") # Disable the "Browse" button
        button_Analyze.configure(state="disabled") # Disable the "Analyze" button
        progress_bar.pack()  # Show the progress bar
        threading.Thread(target = analyze_audio_file, args=(file_path, file_name)).start()
        
    except Exception as e:
        result_label.configure(text=f'Error: {e}')
        button_browse.configure(state="normal") # Re-enable the "Browse" button in case of error
        button_Analyze.configure(state="normal") # Re-enable the "Analyze" button in case of error

def analyze_audio_file(file_path, file_name):
    try:
        progress_var.set(0) # Reset progress bar
        bottom_label.configure(text=f'Status: Start Analyzing 0%')
        net_audio_value = calculate_net_audio(file_path, progress_var)
        result_label.configure(text=f'Result: Net Audio trim just the first 5 minutes is {net_audio_value/1000} seconds.')
        # print(f'Net Audio for the first 5 minutes is {net_audio_value/1000:.4f} seconds.')
        
        # Write results to a log file
        current_app_dir = os.getcwd()
        logs_folder_path = os.path.join(current_app_dir, 'logs')
        current_date = today.strftime(f"%d/%m/%Y %H:%M:%S")
        # bottom_label2.configure(text=f'current logs path: {logs_folder_path}')
        if not os.path.exists(logs_folder_path):
            os.makedirs(logs_folder_path)
            
        log_file = os.path.join(logs_folder_path, (f'net_audio_results_{file_name}.txt'))
        with open(log_file, 'a') as log_file:
            log_file.write(f'Net Audio is {net_audio_value/1000} seconds {current_date}\n')
        bottom_label.configure(text=f'Status: Analyze is done 100% !')
    except Exception as e:
        result_label.configure(text=f'Error: {e}')
    finally:
        button_browse.configure(state="normal") # Re-enable the "Browse" button
        button_Analyze.configure(state="normal") # Re-enable the "Analyze" button

# Create GUI layout
frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

label = customtkinter.CTkLabel(master=frame, text="Browse your file for Analyze and remove silent Audio", font=("Roboto", 18, "bold"))
label.pack(pady=12, padx=10)

result_label = customtkinter.CTkLabel(master=frame, text="Result:", font=("Roboto", 14))
result_label.pack(pady=12, padx=10)

file_name_label = customtkinter.CTkLabel(master=frame, text="File name:", font=("Roboto", 14))
file_name_label.pack(pady=12, padx=10)

entry_filepath = customtkinter.CTkEntry(master=frame, placeholder_text="Browse your .wav file", font=("Roboto", 12))
entry_filepath.pack(pady=12, padx=10)

button_browse = customtkinter.CTkButton(master=frame, text="Browse", command=select_wav_file, font=("Roboto", 16))
button_browse.pack(pady=12, padx=10)

button_Analyze = customtkinter.CTkButton(master=frame, text="Analyze", command=analyze_file, font=("Roboto", 16))
button_Analyze.pack(pady=12, padx=10)

progress_var = customtkinter.DoubleVar()
progress_bar = customtkinter.CTkProgressBar(master=frame, variable=progress_var)
# progress_bar.pack(pady=12, padx=10)
progress_bar.pack_forget()  # Hide the progress bar after the analysis completes

bottom_label = customtkinter.CTkLabel(master=frame, text="Status: Please start !", font=("Roboto", 12))
bottom_label.pack(pady=12, padx=10)
# bottom_label2 = customtkinter.CTkLabel(master=frame, text="current logs path: ?", font=("Roboto", 12))
# bottom_label2.pack(pady=12, padx=10)

root.mainloop()