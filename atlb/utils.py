# AT PROJECT Limited 2022 - 2024; nXRE-v3.7_beta.2
from datetime import datetime

import discord
import wavelink

class Colors:
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    YELLOW = '\033[93m'
    UNDERLINE = '\033[4m'

def truncate_title(title, max_length=65):
    if len(title) > max_length:
        return title[:max_length - 3] + "..."
    
    return title

def send_postinit_message():
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print()
    print(f"  __          {Colors.CYAN}{Colors.BOLD}nXRE {Colors.ENDC}{Colors.YELLOW}Release Lambda{Colors.ENDC}",
          f"{Colors.BOLD}{Colors.CYAN}Version {Colors.ENDC}{Colors.YELLOW}3.7β2{Colors.ENDC}")
    print("  \\ \\")
    print(f"   > \\        {Colors.CYAN}{Colors.BOLD}Start Time:         {Colors.ENDC}{start_time}")
    print(f"  / ^ \\       {Colors.CYAN}{Colors.BOLD}discord.py Version: {Colors.ENDC}{discord.__version__}")
    print(f" /_/ \\_\\      {Colors.CYAN}{Colors.BOLD}wavelink Version:   {Colors.ENDC}{wavelink.__version__}")
    print()