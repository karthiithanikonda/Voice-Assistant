from voice_assistant import speak, process_command

def main():
    speak("Hello, I am your voice assistant. How can I help you?")

    running = True

    while running:
        command = input("\nType your command: ").lower()
        print("You typed:", command)
        running = process_command(command)

if __name__ == "__main__":
    main()