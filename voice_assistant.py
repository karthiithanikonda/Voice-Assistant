
import speech_recognition as sr
import pyttsx3
import wikipedia
import subprocess
import os
import re
import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
import webbrowser

engine=pyttsx3.init()
voices=engine.getProperty("voices")
female_voice=None
for voice in voices:
    name=voice.name.lower()
    voice_id=voice.id.lower()
    if "zira" in name or "zira" in voice_id or "female" in name or "female" in voice_id or "hazel" in name or "hazel" in voice_id:
        female_voice=voice.id
        break
if female_voice:
    engine.setProperty("voice",female_voice)
engine.setProperty("rate",170)
engine.setProperty("volume",1.0)

recognizer=sr.Recognizer()
user_name=""

def speak(text):
    print("Assistant:",text)
    try:
        engine.say(text)
        engine.runAndWait()
    except:
        pass

def find_chrome():
    paths=[
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None

CHROME=find_chrome()

def open_url(url):
    try:
        if CHROME:
            subprocess.Popen([CHROME,"--new-tab",url])
        else:
            webbrowser.open(url)
        return True
    except:
        try:
            webbrowser.open(url)
            return True
        except:
            return False

def listen():
    print("\nListening...")
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source,duration=0.4)
            audio=recognizer.listen(source,timeout=7,phrase_time_limit=15)
        try:
            command=recognizer.recognize_google(audio,language="en-IN").lower().strip()
            print("You:",command)
            return command
        except sr.UnknownValueError:
            speak("Sorry, I could not understand what you said.")
            return ""
        except sr.RequestError:
            speak("I cannot connect to the speech recognition service. Please check your internet connection.")
            return ""
    except sr.WaitTimeoutError:
        return ""
    except:
        speak("I could not access the microphone.")
        return ""

def clean_text(text):
    return re.sub(r"\s+"," ",text).strip()

def remember_name(command):
    global user_name
    match=re.search(r"\bmy name is\s+(.+)",command)
    if not match:
        return False
    name=match.group(1).strip()
    stop_words=[
        "nice to meet you",
        "good to meet you",
        "thank you",
        "thanks",
        "and i am",
        "and i'm",
        "i am",
        "i'm",
        "that's great",
        "thats great",
        "great"
    ]
    for word in stop_words:
        if word in name:
            name=name.split(word)[0].strip()
    name=re.sub(r"[^\w\s'-]","",name)
    words=name.split()
    if len(words)>3:
        name=" ".join(words[:3])
    if name:
        user_name=name.title()
        speak("Nice to meet you, "+user_name+". I will remember your name during this conversation.")
        return True
    return False

def math_expression(text):
    text=text.lower()
    text=text.replace("×","*")
    text=text.replace("÷","/")
    text=text.replace("−","-")
    text=text.replace("–","-")
    text=text.replace("—","-")
    text=re.sub(r"\bx\b","*",text)
    text=text.replace("multiplied by","*")
    text=text.replace("multiply by","*")
    text=text.replace("times","*")
    text=text.replace("into","*")
    text=text.replace("divided by","/")
    text=text.replace("divide by","/")
    text=text.replace("divided","/")
    text=text.replace("divide","/")
    text=text.replace("plus","+")
    text=text.replace("minus","-")
    text=text.replace("add","+")
    text=text.replace("subtract","-")
    text=text.replace("multiply","*")
    text=text.replace("sum of"," ")
    text=text.replace("product of"," ")
    text=text.replace("difference between"," ")
    text=text.replace("what is"," ")
    text=text.replace("what's"," ")
    text=text.replace("calculate"," ")
    text=text.replace("please"," ")
    text=text.replace("can you"," ")
    text=text.replace("tell me"," ")
    text=text.replace("the answer to"," ")
    text=text.replace("the answer"," ")
    text=text.replace("the result of"," ")
    text=text.replace("result"," ")
    text=text.replace("answer"," ")
    text=text.replace("equals"," ")
    text=text.replace("equal to"," ")
    text=re.sub(r"\bthe\b"," ",text)
    text=re.sub(r"\band\b","+ ",text)
    text=clean_text(text)
    text=re.sub(r"[^0-9+\-*/().%\s]","",text)
    text=clean_text(text)
    if not re.search(r"\d",text):
        return None
    if not re.search(r"[\+\-\*/]",text):
        return None
    if not re.fullmatch(r"[0-9+\-*/().%\s]+",text):
        return None
    return text

def calculate(command):
    expression=math_expression(command)
    if not expression:
        return False
    try:
        result=eval(expression,{"__builtins__":None},{})
        if isinstance(result,float):
            if result.is_integer():
                result=int(result)
            else:
                result=round(result,6)
        speak("The answer is "+str(result)+".")
        return True
    except ZeroDivisionError:
        speak("You cannot divide by zero.")
        return True
    except:
        return False

def simple_interest(command):
    numbers=re.findall(r"\d+(?:\.\d+)?",command)
    if len(numbers)<3:
        speak("Please give the principal amount, rate, and time.")
        return True
    p=float(numbers[0])
    r=float(numbers[1])
    t=float(numbers[2])
    interest=p*r*t/100
    amount=p+interest
    speak("The simple interest is "+format(interest,".2f")+" and the total amount is "+format(amount,".2f")+".")
    return True

def compound_interest(command):
    numbers=re.findall(r"\d+(?:\.\d+)?",command)
    if len(numbers)<3:
        speak("Please give the principal amount, rate, and time.")
        return True
    p=float(numbers[0])
    r=float(numbers[1])
    t=float(numbers[2])
    amount=p*((1+r/100)**t)
    interest=amount-p
    speak("The compound interest is "+format(interest,".2f")+" and the total amount is "+format(amount,".2f")+".")
    return True

def profit_loss(command):
    numbers=re.findall(r"\d+(?:\.\d+)?",command)
    if len(numbers)<2:
        speak("Please give the cost price and selling price.")
        return True
    cost=float(numbers[0])
    selling=float(numbers[1])
    if selling>cost:
        profit=selling-cost
        percentage=(profit/cost)*100 if cost else 0
        speak("The profit is "+format(profit,".2f")+" and the profit percentage is "+format(percentage,".2f")+" percent.")
    elif selling<cost:
        loss=cost-selling
        percentage=(loss/cost)*100 if cost else 0
        speak("The loss is "+format(loss,".2f")+" and the loss percentage is "+format(percentage,".2f")+" percent.")
    else:
        speak("There is no profit and no loss.")
    return True

def general_response(command):
    global user_name

    if remember_name(command):
        return True

    if any(x in command for x in ["what is my name","do you remember my name","remember my name","remembering my name"]):
        if user_name:
            speak("Yes. Your name is "+user_name+".")
        else:
            speak("You have not told me your name yet.")
        return True

    if re.search(r"\b(hello|hi|hey)\b",command):
        if user_name:
            speak("Hello "+user_name+"! Nice to talk to you. How can I help you?")
        else:
            speak("Hello! Nice to talk to you. How can I help you?")
        return True

    if "good morning" in command:
        if user_name:
            speak("Good morning, "+user_name+"! I hope you are having a great day.")
        else:
            speak("Good morning! I hope you are having a great day.")
        return True

    if "good afternoon" in command:
        speak("Good afternoon! I hope your day is going well.")
        return True

    if "good evening" in command:
        speak("Good evening! How can I help you?")
        return True

    if "good night" in command:
        speak("Good night! Have a wonderful night.")
        return True

    if "how are you" in command:
        speak("I am doing great. Thank you for asking. How are you?")
        return True

    if "i am fine" in command or "i'm fine" in command or "i am good" in command or "i'm good" in command:
        speak("That's great to hear. I am happy that you are doing well.")
        return True

    if "what is your name" in command or "who are you" in command:
        speak("My name is your voice assistant. You can call me Assistant.")
        return True

    if "thank you" in command or "thanks" in command:
        speak("You're welcome. I am happy to help.")
        return True

    if "nice to meet you" in command:
        if user_name:
            speak("Nice to meet you too, "+user_name+".")
        else:
            speak("Nice to meet you too.")
        return True

    if "i am bored" in command or "i'm bored" in command:
        speak("Let's do something interesting. You can ask me a question, calculation, or tell me to open a website.")
        return True

    if "are you there" in command or "are you listening" in command:
        speak("Yes, I am here and listening.")
        return True

    if "what can you do" in command:
        speak("I can have friendly conversations, perform basic mathematics, calculate interest and profit or loss, tell you the time and date, answer information questions, search Google when you ask, and open websites and Windows applications.")
        return True

    if "tell me a joke" in command:
        speak("Why did the computer go to the doctor? Because it had a virus.")
        return True

    if "are you real" in command:
        speak("I am an artificial intelligence voice assistant running on your computer.")
        return True

    if "sorry" in command:
        speak("That's okay. No problem at all.")
        return True

    if "who made you" in command:
        speak("I am a Python voice assistant created to help you with everyday tasks.")
        return True

    if "i love you" in command:
        speak("That's very kind of you. I am always happy to help.")
        return True

    if command in ["ok","okay","alright","fine","good"]:
        speak("Okay. What would you like me to do?")
        return True

    return False

def get_timezone(command):
    zones={
        "new york":"America/New_York",
        "usa":"America/New_York",
        "united states":"America/New_York",
        "america":"America/New_York",
        "los angeles":"America/Los_Angeles",
        "california":"America/Los_Angeles",
        "chicago":"America/Chicago",
        "london":"Europe/London",
        "uk":"Europe/London",
        "united kingdom":"Europe/London",
        "dubai":"Asia/Dubai",
        "uae":"Asia/Dubai",
        "singapore":"Asia/Singapore",
        "tokyo":"Asia/Tokyo",
        "japan":"Asia/Tokyo",
        "sydney":"Australia/Sydney",
        "australia":"Australia/Sydney",
        "paris":"Europe/Paris",
        "france":"Europe/Paris",
        "berlin":"Europe/Berlin",
        "germany":"Europe/Berlin",
        "toronto":"America/Toronto",
        "canada":"America/Toronto",
        "india":"Asia/Kolkata",
        "delhi":"Asia/Kolkata",
        "mumbai":"Asia/Kolkata",
        "hyderabad":"Asia/Kolkata",
        "guntur":"Asia/Kolkata"
    }
    for name,zone in zones.items():
        if name in command:
            return zone,name
    return None,None

def tell_time(command):
    zone,name=get_timezone(command)
    if zone:
        now=datetime.now(ZoneInfo(zone))
        speak("The current time in "+name+" is "+now.strftime("%I:%M %p")+".")
    else:
        speak("The current time is "+datetime.now().strftime("%I:%M %p")+".")
    return True

def tell_date():
    speak("Today is "+datetime.now().strftime("%d %B %Y")+".")
    return True

def wikipedia_answer(command):
    q=command
    remove=[
        "who is",
        "who was",
        "what is",
        "what are",
        "what was",
        "what were",
        "tell me about",
        "explain",
        "define",
        "definition of",
        "information about",
        "information on",
        "wikipedia"
    ]
    for word in remove:
        q=q.replace(word," ")
    q=clean_text(q)
    if not q:
        return False
    try:
        result=wikipedia.summary(q,sentences=3,auto_suggest=True)
        speak(result)
        return True
    except wikipedia.exceptions.DisambiguationError as e:
        try:
            if e.options:
                result=wikipedia.summary(e.options[0],sentences=3)
                speak(result)
                return True
        except:
            pass
    except:
        pass
    return False

def google_search(command):
    q=command
    remove=[
        "check in google for",
        "check on google for",
        "check google for",
        "search google for",
        "search google",
        "search for",
        "google search for",
        "look up on google",
        "look up",
        "google"
    ]
    for word in remove:
        q=q.replace(word," ")
    q=clean_text(q)
    if not q:
        q="Google"
    speak("Searching Google for "+q)
    open_url("https://www.google.com/search?q="+urllib.parse.quote(q))
    return True

def youtube(command):
    q=command
    remove=[
        "open youtube",
        "youtube",
        "play",
        "watch",
        "video",
        "song",
        "music",
        "on youtube",
        "please"
    ]
    for word in remove:
        q=q.replace(word," ")
    q=clean_text(q)
    if not q:
        open_url("https://www.youtube.com")
        speak("Opening YouTube.")
        return True
    speak("Searching YouTube for "+q)
    open_url("https://www.youtube.com/results?search_query="+urllib.parse.quote(q))
    return True

def google_images(command):
    q=command
    remove=[
        "show me",
        "show",
        "images of",
        "image of",
        "pictures of",
        "picture of",
        "pics of",
        "pics",
        "images",
        "pictures"
    ]
    for word in remove:
        q=q.replace(word," ")
    q=clean_text(q)
    if not q:
        return False
    speak("Opening images of "+q)
    open_url("https://www.google.com/search?tbm=isch&q="+urllib.parse.quote(q))
    return True

def maps(command):
    q=command
    for word in ["google maps","open maps","maps","show location of","location of"]:
        q=q.replace(word," ")
    q=clean_text(q)
    if not q:
        open_url("https://www.google.com/maps")
        speak("Opening Google Maps.")
        return True
    speak("Opening Google Maps for "+q)
    open_url("https://www.google.com/maps/search/?api=1&query="+urllib.parse.quote(q))
    return True

def navigate(command):
    q=command
    for word in ["navigate to","directions to","take me to","go to","route to","drive to"]:
        q=q.replace(word," ")
    q=clean_text(q)
    if not q:
        speak("Please tell me the destination.")
        return True
    speak("Opening directions to "+q)
    open_url("https://www.google.com/maps/dir/?api=1&destination="+urllib.parse.quote(q)+"&travelmode=driving")
    return True

def open_site(command):
    sites={
        "linkedin":"https://www.linkedin.com",
        "instagram":"https://www.instagram.com",
        "facebook":"https://www.facebook.com",
        "whatsapp":"https://web.whatsapp.com",
        "youtube":"https://www.youtube.com",
        "twitter":"https://x.com",
        "x":"https://x.com",
        "telegram":"https://web.telegram.org",
        "reddit":"https://www.reddit.com",
        "github":"https://github.com",
        "discord":"https://discord.com/app",
        "pinterest":"https://www.pinterest.com",
        "snapchat":"https://web.snapchat.com",
        "threads":"https://www.threads.net",
        "gmail":"https://mail.google.com",
        "google drive":"https://drive.google.com",
        "google docs":"https://docs.google.com",
        "google sheets":"https://sheets.google.com",
        "google meet":"https://meet.google.com",
        "google classroom":"https://classroom.google.com",
        "google":"https://www.google.com",
        "bing":"https://www.bing.com",
        "amazon":"https://www.amazon.in",
        "flipkart":"https://www.flipkart.com",
        "myntra":"https://www.myntra.com",
        "meesho":"https://www.meesho.com",
        "netflix":"https://www.netflix.com",
        "prime video":"https://www.primevideo.com",
        "hotstar":"https://www.hotstar.com",
        "spotify":"https://open.spotify.com",
        "canva":"https://www.canva.com",
        "chatgpt":"https://chatgpt.com",
        "openai":"https://openai.com",
        "stackoverflow":"https://stackoverflow.com",
        "leetcode":"https://leetcode.com",
        "codechef":"https://www.codechef.com",
        "hackerrank":"https://www.hackerrank.com",
        "geeksforgeeks":"https://www.geeksforgeeks.org",
        "coursera":"https://www.coursera.org",
        "udemy":"https://www.udemy.com",
        "wikipedia":"https://www.wikipedia.org",
        "python":"https://www.python.org",
        "npm":"https://www.npmjs.com",
        "pypi":"https://pypi.org",
        "google colab":"https://colab.research.google.com",
        "calendar":"https://calendar.google.com"
    }
    for name,url in sorted(sites.items(),key=lambda x:len(x[0]),reverse=True):
        if name in command:
            speak("Opening "+name+".")
            if open_url(url):
                return True
            speak("I could not open "+name+".")
            return True
    return False

def open_windows_app(command):
    apps={
        "notepad":"notepad.exe",
        "calculator":"calc.exe",
        "calc":"calc.exe",
        "file explorer":"explorer.exe",
        "explorer":"explorer.exe",
        "command prompt":"cmd.exe",
        "cmd":"cmd.exe",
        "powershell":"powershell.exe",
        "paint":"mspaint.exe",
        "task manager":"taskmgr.exe",
        "control panel":"control.exe"
    }
    for name,exe in sorted(apps.items(),key=lambda x:len(x[0]),reverse=True):
        if name in command:
            speak("Opening "+name+".")
            try:
                subprocess.Popen(exe)
            except:
                speak("I could not open "+name+".")
            return True

    if "visual studio code" in command or "vs code" in command:
        paths=[
            os.path.expandvars(r"%LocalAppData%\Programs\Microsoft VS Code\Code.exe"),
            os.path.expandvars(r"%ProgramFiles%\Microsoft VS Code\Code.exe")
        ]
        for path in paths:
            if os.path.exists(path):
                speak("Opening Visual Studio Code.")
                subprocess.Popen([path])
                return True
        try:
            subprocess.Popen(["code"])
            speak("Opening Visual Studio Code.")
        except:
            speak("Visual Studio Code is not installed or is not available in PATH.")
        return True

    return False

def explicit_open(command):
    triggers=[
        "open ",
        "go to ",
        "visit ",
        "launch ",
        "start "
    ]

    if not any(command.startswith(x) for x in triggers):
        return False

    if "youtube" in command and any(x in command for x in ["play","watch","song","video","music"]):
        return youtube(command)

    if any(x in command for x in ["maps","google maps"]):
        return maps(command)

    if any(x in command for x in ["navigate to","directions to","take me to","route to","drive to"]):
        return navigate(command)

    if open_windows_app(command):
        return True

    if open_site(command):
        return True

    if command.startswith("open chrome") or command.startswith("open browser"):
        speak("Opening Google Chrome.")
        open_url("https://www.google.com")
        return True

    q=command
    for word in ["open","go to","visit","launch","start"]:
        q=q.replace(word," ")
    q=clean_text(q)

    if q:
        speak("I do not have a direct link for "+q+". Please say search Google for "+q+" if you want me to search for it.")
        return True

    speak("What would you like me to open?")
    return True

def process(command):
    if not command:
        return True

    command=clean_text(command.lower())
    print("Processing:",command)

    if any(x in command for x in ["exit","quit","stop assistant","close assistant","goodbye","bye"]):
        speak("Goodbye. Have a great day.")
        return False

    if general_response(command):
        return True

    if "simple interest" in command:
        return simple_interest(command)

    if "compound interest" in command:
        return compound_interest(command)

    if ("profit" in command or "loss" in command) and len(re.findall(r"\d+(?:\.\d+)?",command))>=2:
        return profit_loss(command)

    if "time" in command:
        return tell_time(command)

    if "date" in command or "today" in command:
        return tell_date()

    if ("play" in command or "watch" in command) and ("youtube" in command or "song" in command or "video" in command):
        return youtube(command)

    if command.startswith("play "):
        return youtube(command)

    if any(x in command for x in ["image","images","picture","pictures","pics"]):
        return google_images(command)

    if any(x in command for x in ["navigate to","directions to","take me to","route to","drive to"]):
        return navigate(command)

    if explicit_open(command):
        return True

    if calculate(command):
        return True

    if command.startswith("search google") or command.startswith("check google") or command.startswith("check in google") or command.startswith("check on google") or command.startswith("google search") or command.startswith("look up on google"):
        return google_search(command)

    if command.startswith("search for") or command.startswith("search "):
        return google_search(command)

    if any(x in command for x in ["who is","who was","what is","what are","what was","what were","tell me about","explain","define","definition of","information about","information on"]):
        if wikipedia_answer(command):
            return True
        speak("I could not find a direct answer to that question. If you want, say search Google for it.")
        return True

    speak("I did not understand that clearly. Please say it again.")
    return True

def main():
    if CHROME:
        speak("Hello. Your voice assistant is ready. Google Chrome is ready.")
    else:
        speak("Hello. Your voice assistant is ready. I could not find Google Chrome, so I will use your default browser.")

    while True:
        command=listen()
        running=process(command)
        if not running:
            break

if __name__=="__main__":
    main()

