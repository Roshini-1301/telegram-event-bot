# Run daily PowerShell script to execute the bot.
# To schedule this script, create a Task Scheduler entry that runs this PowerShell script daily.

Set-Location -Path "C:\Users\roshi\OneDrive\Documents\tele bot"
# Optional: activate virtualenv if you use one, e.g.
# & "C:\Users\roshi\Envs\telebot\Scripts\Activate.ps1"

# Run the main Python script
python main.py
