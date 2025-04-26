using_terminator = False
take_picture_flag = {"capture": False}
global camera_running
import datetime
import pytz
import os
import webbrowser
import openai
import re
import threading
#import pyaudio
import smtplib
import subprocess
import opencv.python as cv2
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import platform
import glob
from urllib.parse import quote
import pyautogui
searching = True
listening_for_interrupt = False
stop_speaking = False
expecting_code = False
import streamlit as st
import speech_recognition as sr
import pyttsx3
import time
st.set_page_config(page_title="🎙 SAGE Assistant", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
<style>
/* Background gradient */
body, .stApp {
    background: linear-gradient(135deg, #00b4db, #0083b0);
    background-attachment: fixed;
    color: black;
    font-family: 'Segoe UI', sans-serif;
}

/* Glass effect container */
section.main > div {
    background: rgba(255, 255, 255, 0.07);
    border-radius: 16px;
    padding: 30px;
    box-shadow: 0 0 20px rgba(0, 200, 255, 0.2);
    backdrop-filter: blur(6px);
}

/* Typing animation */
.typing {
  width: 100%;
  white-space: nowrap;
  overflow: hidden;
  border-right: 4px solid #ff8c00;
  animation: typing 3s steps(40, end), blink .75s step-end infinite;
  font-size: 20px;
  font-weight: bold;
  font-family: monospace;
  color: white;
  margin-top: 10px;
}
@keyframes typing {
  from { width: 0 }
  to { width: 100% }
}
@keyframes blink {
  50% { border-color: transparent }
}

/* Button hover */
button[kind="primary"] {
    background-color: #0099cc !important;
    color: white !important;
    border-radius: 8px !important;
    display: flex; justify-content: center;
}
button[kind="primary"]:hover {
    background-color: #007acc !important;
}
</style>
""", unsafe_allow_html=True)

# --- UI Content ---
st.markdown("<h1 style='text-align: center;'>🤖 SAGE - Your AI DESKTOP Voice Assistant</h1>", unsafe_allow_html=True)
st.markdown("<div class='typing'>Hello, I'm SAGE. Ready to take your command.</div>", unsafe_allow_html=True)
st.markdown("---")
engine = pyttsx3.init()
voices = engine.getProperty('voices')


voices = engine.getProperty('voices')
preferred_voice_index = 1
if len(voices) > preferred_voice_index:
    engine.setProperty('voice', voices[preferred_voice_index].id)
else:
    engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 170)

def say(text):
    print("Sage\n", text)
    engine.say(text)
    engine.runAndWait()

def send_email(subject, body, to_email):
    from_email = "gppg317@gmail.com"
    password = "AGboy@@2001"

    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, message.as_string())
        server.quit()
        say("Email has been sent successfully.")
        print("Email sent!")
    except Exception as e:
        say("Sorry, I was not able to send the email.")
        print("Email sending error:", e)

def ai(prompt):
    try:
        openai.api_key = "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"
        openai.api_base = "https://api.groq.com/openai/v1"
        model_name = "llama3-8b-8192"

        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        reply = response['choices'][0]['message']['content']
        print("AI Response:", reply)
        return reply

    except Exception as e:
        print(f"AI Error: {e}")
        return "Sorry, I encountered an error processing your request."


def chat(prompt):
    global searching
    if not searching:
        return "Searching is currently paused. Say 'start searching' to resume."
    try:
        openai.api_key = "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"
        openai.api_base = "https://api.groq.com/openai/v1"
        model_name = "llama3-8b-8192"

        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        reply = response['choices'][0]['message']['content']
        #print("Chat Response:", reply)
        say(reply)
        return reply

    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        say(error_msg)
        print(f"Chat Error: {e}")
        return error_msg

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your command...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-in")  # Indian English
        print(f"User said: {query}")
        return query.lower()

    except sr.RequestError:
        error_msg = "Error: Unable to connect to the speech recognition service."
        print(error_msg)
        say(error_msg)
        return error_msg

    except sr.UnknownValueError:
        error_msg = "Sorry, I couldn't understand what you said."
        print(error_msg)
        say(error_msg)
        return error_msg

    except Exception as e:
        print("Sorry, I could not recognize your voice.")
        return None


def open_app(command):
    app_mapping = {
        "excel": "excel",
        "powerpoint": "powerpnt",
        "word": "winword",
        "notepad": "notepad",
        "settings": "ms-settings:",
        "calculator": "calc",
        "paint": "mspaint",
        "chrome": "chrome",
        "command prompt": "cmd",
        "vscode": "code"
    }

    command = command.lower()

    for app, app_name in app_mapping.items():
        if app in command:
            try:
                print(f"Attempting to open {app_name}...")
                subprocess.run([app_name], check=True)
                print(f"{app_name} launched successfully.")
                say(f"Opening {app.capitalize()}.")
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error opening {app_name}: {e}")
                say(f"Could not open {app.capitalize()}.")
                return False

    say("Sorry, I don't recognize that app.")
    return False


def get_current_time():
    india = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(india)
    return now.strftime("%I:%M %p")

def get_current_date():
    india = pytz.timezone('Asia/Kolkata')
    today = datetime.datetime.now(india)
    return today.strftime("%A, %d %B %Y")

def open_music():
    music_folder = os.path.join(os.path.expanduser("~"), "Music")
    music_files = glob.glob(os.path.join(music_folder, "*.mp3"))
    if music_files:
        file_to_play = music_files[0]
        if platform.system() == "Windows":
            os.startfile(file_to_play)
        elif platform.system() == "Darwin":
            subprocess.call(["open", file_to_play])
        else:
            subprocess.call(["xdg-open", file_to_play])
        say("Playing music now.")
    else:
        say("Sorry, I couldn't find any music files.")

def use_terminator(command):
    try:
        result = subprocess.run(["terminator"] + command.split(), capture_output=True, text=True)
        print("Terminator Output:", result.stdout)
        say("Command executed using Terminator.")
    except Exception as e:
        print("Error running Terminator:", e)
        say("Failed to execute Terminator command.")


def run_in_terminator_mode(command):
    global using_terminator
    say("Processing your request in Terminator mode.")
    print(f"[TERMINATOR] Executing: {command}")
    if open_app(command):
        return



    if "write" in command.lower() and "notepad" in command.lower():
        topic_match = re.search(r'write (about|a|an|the)?(.*)', command.lower())
        topic = topic_match.group(2).strip() if topic_match else "something interesting"
        prompt = f"Write a paragraph about {topic}."
        content = ai(prompt)
        file_path = os.path.join(os.getcwd(), "terminator_output.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.system(f'start notepad.exe "{file_path}"')
        say("I've written about that in Notepad for you.")


    elif "play" in command.lower() and "youtube" in command.lower():
        query = command.lower().replace("play", "").replace("on youtube", "").strip()
        search_query = quote(query)
        url = f"https://www.youtube.com/results?search_query={search_query}"
        webbrowser.open(url)
        say(f"Searching YouTube for {query} and playing it.")
        time.sleep(6)
        pyautogui.moveTo(330, 350)
        pyautogui.click()

    elif "open gmail" in command.lower():
        webbrowser.open("https://mail.google.com")
        say("Opening Gmail.")


    elif "open" in command.lower() and "website" in command.lower():
        match = re.search(r'open (.*?) website', command.lower())
        site = match.group(1).strip().replace(" ", "")
        url = f"https://{site}.com"
        webbrowser.open(url)
        say(f"Opening {site} website.")
    elif "search" in command.lower():
        search_term = command.lower().replace("search", "").strip()
        search_query = quote(search_term)
        url = f"https://www.google.com/search?q={search_query}"
        webbrowser.open(url)
        say(f"Searching Google for {search_term}.")


    elif "check unread email" in command.lower() or "analyze unread email" in command.lower():
        import imaplib
        import email
        from email.header import decode_header
        username = "mayankbaghel240202005@gmail.com"
        password = "xdbo qfzk bswf djnj"
        def clean(text):
            return "".join(c if c.isalnum() else "_" for c in text)

        say("Checking unread emails...")
        imap = imaplib.IMAP4_SSL("imap.gmail.com")

        try:
            imap.login(username, password)
            imap.select("inbox")
            status, messages = imap.search(None, '(UNSEEN)')
            email_ids = messages[0].split()

            if not email_ids:
                say("No unread emails found.")
            else:
                say(f"You have {len(email_ids)} unread emails.")
                for i, mail_id in enumerate(email_ids[:5], 1):
                    status, msg_data = imap.fetch(mail_id, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            subject, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding if encoding else "utf-8")
                                from_ = msg.get("From")
                            say(f"Email {i} is from {from_} with subject: {subject}")
                            if msg.is_multipart():
                                   for part in msg.walk():
                                       if part.get_content_type() == "text/plain":
                                           body = part.get_payload(decode=True).decode()
                                           print(f"Body:\n{body}\n")
                                           break
                            else:
                                body = msg.get_payload(decode=True).decode()
                                print(f"Body:\n{body}\n")

        except Exception as e:
            say("Failed to check emails.")
            print("Error:", e)
        finally:
            imap.logout()


def play_youtube_music(query, pyautogui=None):
    search_query = quote(query)
    url = f"https://www.youtube.com/results?search_query={search_query}"
    webbrowser.open(url)
    say(f"Searching YouTube for {query} and playing first music.")
    time.sleep(5)
    if pyautogui:
        pyautogui.press("tab", presses=6)
        pyautogui.press("enter")

def open_file_by_name(name):
    user_home = os.path.expanduser("~")
    search_paths = [
        os.path.join(user_home, "Desktop"),
        os.path.join(user_home, "Documents"),
        os.path.join(user_home, "Downloads"),
        user_home
    ]
    found = False
    for path in search_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if name.lower() in file.lower():
                    file_path = os.path.join(root, file)
                    say(f"Opening file: {file}")
                    os.startfile(file_path)
                    return True
            for folder in dirs:
                if name.lower() in folder.lower():
                    folder_path = os.path.join(root, folder)
                    say(f"Opening folder: {folder}")
                    os.startfile(folder_path)
                    return True
    say("Sorry, I couldn't find any matching files or folders.")
    return False
def open_camera():
    def camera_thread():
        global camera_running
        camera_running = True
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Camera could not be opened.")
            return

        print("Camera opened. Showing preview for 10 seconds...")
        start_time = time.time()

        while camera_running:  # <- Change is here
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break
            cv2.imshow("System Camera", frame)

            if time.time() - start_time > 10:
                print("Closing camera preview.")
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("User pressed 'q'.")
                break

        cap.release()
        cv2.destroyAllWindows()

    threading.Thread(target=camera_thread, daemon=True).start()
    say("Opening your camera now.")

if __name__ == '__main__':
    say("Hello My name is Sage")
    print('Sage')
    while True:
        print("Listening.....")
        query = takecommand()
        if (
                not query
                or "couldn't understand" in query.lower()
                or "error" in query.lower()
                or "none" == query.lower().strip()
                or len(query.strip()) < 3
        ):
            print("No valid command recognized. Skipping...\n")
            say("Sorry, I didn't catch that. Please say it again.")
            continue
        if "use terminator" in query.lower() or (query.lower().strip() == "terminator"):
            using_terminator = True
            say("What should I do in the terminal?")
            continue
        if using_terminator:
            if query is None:
                continue

            query = query.lower().strip()

            if "stop terminator" in query or "exit terminator" in query or "leave terminal" in query:
                say("Exiting Terminator mode.")
                using_terminator = False
                continue

            run_in_terminator_mode(query)
            continue


        if "i want to type" in query.lower():
            say("Okay, switching to text mode. Please type your command.")
            query = input("Enter your command: ")

        if "play" in query and "youtube" in query:
            video_query = query.lower().replace("play", "").replace("on youtube", "").strip()
            play_youtube_music(video_query, pyautogui)
            continue

        if "use terminator" in query.lower():
            if using_terminator:
                using_terminator = True

        if expecting_code:
            if "type" in query.lower():
                say("Paste your code. Type 'done' when you're finished.")
                code_lines = []
                while True:
                    line = input()
                    if line.strip().lower() == "done":
                        break
                    code_lines.append(line)
                full_code = "\n".join(code_lines)
            else:
                say("Please speak your code. Say 'done' when you're finished.")
                code_lines = []
                while True:
                    line = takecommand()
                    if "done" in line.lower():
                        break
                    line = line.replace("colon", ":").replace("indent", "    ").replace("open parenthesis", "(").replace("close parenthesis", ")")
                    code_lines.append(line)
                full_code = "\n".join(code_lines)
            corrected_code = ai(f"Please correct the following Python code:\n\n{full_code}")
            say("Here's the corrected version.")
            print("Corrected Code:\n", corrected_code)
            expecting_code = False
            continue

        if "correct my code" in query.lower():
            say("Okay, would you like to type or speak your code?")
            expecting_code = True
            continue

        print("Processing query:", query)

        if "stop searching" in query.lower():
            searching = False
            say("I've paused searching. Say 'start searching' to resume.")
            continue
        elif "start searching" in query.lower():
            searching = True
            say("I've resumed searching. How can I help you?")
            continue

        if "exit youtube" in query.lower() or "close youtube" in query.lower():
            say("Closing the YouTube tab.")
            pyautogui.hotkey('ctrl', 'w')
            continue

        skip_processing = False
        def search_google(query):
            search_query = quote(query)
            url = f"https://www.google.com/search?q={search_query}"
            webbrowser.open(url)
            say(f"Searching Google for {query}.")

        apps = [["game", r'start "" "C:\\Users\\Public\\Desktop\\Grand Theft Auto V.lnk"'], ["music", open_music], ["notepad", r'start "" "C:\\Windows\\notepad.exe"'], ["gallery", r'start "" "C:\\Users\\irsha\\OneDrive\\Pictures"']]
        for app in apps:
            if f"open {app[0]}" in query.lower():
                say(f"Starting {app[0]}, sir...")
                if callable(app[1]):
                    app[1]()
                else:
                    os.system(app[1])
                skip_processing = True

        if "the time" in query.lower():
            current_time = get_current_time()
            say(f"Sir, the time is {current_time}")
            print(f"Current time: {current_time}")
            skip_processing = True

        if "the date" in query.lower():
            current_date = get_current_date()
            say(f"Sir, today is {current_date}")
            print(f"Current date: {current_date}")
            skip_processing = True
        if "play" in query and "youtube" in query:
            video_query = query.lower().replace("play", "").replace("on youtube", "").strip()
            play_youtube_music(video_query, pyautogui)
            continue


        if any(x in query.lower() for x in ["exit", "quit", "good bye", "bye"]):
            say("Goodbye sir!")
            print("sage shutting down...")
            break

        if "open file" in query.lower() or "open image" in query.lower() or "open pdf" in query.lower() or "open music" in query.lower():
            say("Which file should I open?")
            file_name = takecommand()
            open_file_by_name(file_name)
            continue
        elif "open camera" in query:
            pyttsx3.speak("Opening your camera now.")
            open_camera()
            continue
        elif "close camera" in query or "stop camera" in query:
            global camera_running
            camera_running = False
            say("Camera has been closed.")

        if skip_processing:
            continue

        print("Processing query:", query)

        if "using ai" in query.lower():
            response = ai(query)
            print("AI output:", response)
            say(response)
        elif searching:
            response = chat(query)
            print("Chat output:", response)
