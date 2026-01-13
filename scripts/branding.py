
import sys

def print_banner():
    banner = r"""
    ___    _   __________  ________  ___ _    ____ _______  __
   /   |  / | / /_  __/ / / / ____/ /   | |  / / /_  __/\ \/ /
  / /| | /  |/ / / / / /_/ / / __  / /| | | / / / / /    \  / 
 / ___ |/ /|  / / / / __  / /_/ / / ___ | |/ / / / /     / /  
/_/  |_/_/ |_/ /_/ /_/ /_/\____/ /_/  |_|___/ /_/ /     /_/   
                                                              
    >>> AGENTIC POWER UNLEASHED <<<
    """
    print("\033[1;34m" + banner + "\033[0m")
    print("\033[0;32mSystem initialized. Using DeepSeek engine.\033[0m")
    print("\033[0;36mWelcome, Administrator.\033[0m")

if __name__ == "__main__":
    print_banner()
