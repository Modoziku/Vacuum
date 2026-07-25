import requests
import itertools
import string
import time
import os
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

class UsernameScanner:
    def __init__(self):
        self.found = []
        self.checked = 0
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def log(self, message, color=Fore.WHITE):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Fore.WHITE}[{timestamp}] {color}{message}{Style.RESET_ALL}")

    def generate_usernames(self, keywords, min_len=5, max_len=16, digits_allowed=True):
        chars = string.ascii_lowercase
        if digits_allowed:
            chars += string.digits

        generated = set()

        for keyword in keywords:
            keyword = keyword.lower().strip()
            if not keyword:
                continue

            remaining = max_len - len(keyword)
            if remaining < 0:
                continue

            for prefix_len in range(max(0, min_len - len(keyword)), remaining + 1):
                suffix_len = max_len - len(keyword) - prefix_len
                total_len = prefix_len + len(keyword) + suffix_len

                if total_len < min_len or total_len > max_len:
                    continue

                for prefix in itertools.product(chars, repeat=prefix_len) if prefix_len > 0 else [()]:
                    for suffix in itertools.product(chars, repeat=suffix_len) if suffix_len > 0 else [()]:
                        username = ''.join(prefix) + keyword + ''.join(suffix)
                        if username[0] in string.ascii_lowercase:
                            generated.add(username)

                        if len(generated) >= 100000:
                            return list(generated)

        return list(generated)

    def check_telegram(self, username):
        try:
            url = f"https://t.me/{username}"
            response = self.session.get(url, timeout=5, allow_redirects=False)

            if response.status_code == 302:
                return "free"
            elif response.status_code == 200:
                if "tgme_page_title" in response.text:
                    return "taken"
                return "free"
            return "free"
        except:
            return "unknown"

    def check_fragment(self, username):
        try:
            url = f"https://fragment.com/username/{username}"
            response = self.session.get(url, timeout=5)

            if response.status_code == 404:
                return "free"
            elif "available" in response.text.lower():
                return "free"
            elif "owned" in response.text.lower() or "price" in response.text.lower():
                return "taken"
            return "free"
        except:
            return "unknown"

    def calculate_rarity(self, username):
        score = 0
        length = len(username)

        if length <= 4:
            score += 60
        elif length <= 5:
            score += 50
        elif length <= 7:
            score += 35
        elif length <= 10:
            score += 20
        else:
            score += 10

        has_digits = any(c.isdigit() for c in username)
        has_letters = any(c.isalpha() for c in username)

        if has_letters and not has_digits:
            score += 50
        elif has_letters and has_digits:
            score += 25

        common = [
            "god", "king", "lord", "boss", "dark", "fire", "ice", "sky",
            "max", "pro", "dev", "bot", "fox", "cat", "dog", "x", "hack",
            "net", "web", "app", "art", "lab", "hub", "box", "zen", "one",
            "soul", "evil", "holy", "pure", "void", "star", "moon", "sun",
            "ghost", "angel", "demon", "ninja", "wolf", "lion", "bear"
        ]
        for word in common:
            if word in username.lower():
                score += 25
                break

        if score >= 85:
            return "LEGENDARY", score
        elif score >= 55:
            return "RARE", score
        elif score >= 30:
            return "UNCOMMON", score
        else:
            return "COMMON", score

    def rarity_color(self, rarity):
        if rarity == "LEGENDARY":
            return Fore.YELLOW + Style.BRIGHT
        elif rarity == "RARE":
            return Fore.CYAN + Style.BRIGHT
        elif rarity == "UNCOMMON":
            return Fore.GREEN
        else:
            return Fore.WHITE

    def save_result(self, username, rarity, score, sources):
        with open("free_usernames.txt", "a") as f:
            f.write(f"{username} | {rarity} ({score}) | Free on: {', '.join(sources)}\n")

    def scan_forever(self, keywords, min_len=5, max_len=16, digits_allowed=True):
        self.found = []
        self.checked = 0
        start_time = time.time()

        self.log(f"Keywords: {', '.join(keywords)}", Fore.MAGENTA)
        self.log(f"Length: {min_len}-{max_len} | Digits: {'Yes' if digits_allowed else 'No'}", Fore.MAGENTA)
        self.log("Generating usernames...", Fore.MAGENTA)

        usernames = self.generate_usernames(keywords, min_len, max_len, digits_allowed)
        self.log(f"Generated {len(usernames)} usernames. Scanning forever...", Fore.MAGENTA)
        self.log("Press Ctrl+C to stop.\n", Fore.YELLOW)

        try:
            for username in usernames:
                self.checked += 1

                tg = self.check_telegram(username)
                time.sleep(0.2)

                frag = self.check_fragment(username)
                time.sleep(0.2)

                sources = []
                if tg == "free":
                    sources.append("TG")
                if frag == "free":
                    sources.append("FRAG")

                if sources:
                    rarity, score = self.calculate_rarity(username)
                    self.found.append((username, rarity, score, sources))
                    self.save_result(username, rarity, score, sources)

                    color = self.rarity_color(rarity)
                    self.log(
                        f"🎯 @{username} | {rarity} ({score}) | {', '.join(sources)}",
                        color
                    )

                if self.checked % 50 == 0:
                    elapsed = time.time() - start_time
                    self.log(
                        f"Checked: {self.checked} | Found: {len(self.found)} | {elapsed:.0f}s",
                        Fore.WHITE
                    )

        except KeyboardInterrupt:
            elapsed = time.time() - start_time
            self.log("", Fore.WHITE)
            self.log("=" * 50, Fore.WHITE)
            self.log(f"SCAN STOPPED", Fore.YELLOW)
            self.log(f"Checked: {self.checked} | Found: {len(self.found)} | {elapsed:.0f}s", Fore.WHITE)
            self.log("=" * 50, Fore.WHITE)

            if self.found:
                self.log("BEST FINDS:", Fore.GREEN)
                for username, rarity, score, sources in sorted(self.found, key=lambda x: x[2], reverse=True)[:20]:
                    color = self.rarity_color(rarity)
                    self.log(f"  @{username} | {rarity} ({score}) | {', '.join(sources)}", color)

def main():
    print(Fore.CYAN + "=" * 50)
    print(Fore.CYAN + "   USERNAME SCANNER v2.0")
    print(Fore.CYAN + "=" * 50)
    print()

    while True:
        scanner = UsernameScanner()

        keywords_input = input(Fore.WHITE + "Keywords (comma, e.g. 'moon,star'): ").strip()
        keywords = [k.strip().lower() for k in keywords_input.split(',') if k.strip()]

        if not keywords:
            print(Fore.RED + "Enter at least one keyword.")
            continue

        min_len = input("Min length (5): ").strip()
        min_len = int(min_len) if min_len else 5

        max_len = input("Max length (16): ").strip()
        max_len = int(max_len) if max_len else 16

        digits = input("Allow digits? (y/n, default y): ").strip().lower() != 'n'

        print()
        scanner.scan_forever(keywords, min_len, max_len, digits)

        again = input(Fore.WHITE + "\nNew scan with different keywords? (y/n): ").strip().lower()
        if again != 'y':
            print(Fore.CYAN + "Goodbye!")
            break
        print()

if __name__ == "__main__":
    main()
