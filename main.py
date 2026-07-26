import requests
import itertools
import string
import time
import os
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

PREFIXES = [
    "official", "team", "its", "the", "real", "mr", "ms", "dr",
    "x", "xx", "pro", "super", "mega", "ultra", "hyper", "neo",
    "dark", "light", "holy", "evil", "lord", "king", "boss",
    "og", "xyz", "max", "prime", "elite", "alpha", "omega",
    "zen", "neo", "nova", "zero", "one"
]

SUFFIXES = [
    "hub", "lab", "box", "app", "net", "web", "dev", "art",
    "studio", "official", "team", "hq", "world", "space",
    "verse", "land", "city", "life", "time", "work", "play",
    "x", "xx", "pro", "max", "plus", "ultra", "prime",
    "tv", "fm", "io", "co", "me", "gg", "xyz"
]

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

    def generate_usernames(self, keywords, min_len=5, max_len=16, digits_allowed=True, use_affixes=True):
        chars = string.ascii_lowercase
        if digits_allowed:
            chars += string.digits

        generated = set()

        for keyword in keywords:
            keyword = keyword.lower().strip()
            if not keyword:
                continue

            if min_len <= len(keyword) <= max_len and keyword[0] in string.ascii_lowercase:
                generated.add(keyword)

            if len(keyword) < min_len:
                needed = min_len - len(keyword)
                for prefix in itertools.product(chars, repeat=needed):
                    username = ''.join(prefix) + keyword
                    if username[0] in string.ascii_lowercase:
                        generated.add(username)
                for suffix in itertools.product(chars, repeat=needed):
                    username = keyword + ''.join(suffix)
                    if username[0] in string.ascii_lowercase:
                        generated.add(username)

            if use_affixes:
                for prefix in PREFIXES:
                    username = prefix + keyword
                    if min_len <= len(username) <= max_len and username[0] in string.ascii_lowercase:
                        generated.add(username)
                    for suffix in SUFFIXES:
                        username = prefix + keyword + suffix
                        if min_len <= len(username) <= max_len and username[0] in string.ascii_lowercase:
                            generated.add(username)

                for suffix in SUFFIXES:
                    username = keyword + suffix
                    if min_len <= len(username) <= max_len and username[0] in string.ascii_lowercase:
                        generated.add(username)

                for prefix in PREFIXES:
                    for sep in ['', '_', '.']:
                        username = prefix + sep + keyword
                        if min_len <= len(username) <= max_len and username[0] in string.ascii_lowercase:
                            generated.add(username)

                for suffix in SUFFIXES:
                    for sep in ['', '_', '.']:
                        username = keyword + sep + suffix
                        if min_len <= len(username) <= max_len and username[0] in string.ascii_lowercase:
                            generated.add(username)

            if len(generated) < 1000:
                remaining = max_len - len(keyword)
                if remaining > 0:
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
                                if len(generated) >= 50000:
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
            "ghost", "angel", "demon", "ninja", "wolf", "lion", "bear",
            "official", "team", "studio", "world", "prime", "elite", "alpha"
        ]
        for word in common:
            if word in username.lower():
                score += 25
                break

        if score >= 85:
            return "GOD", score
        elif score >= 65:
            return "LEGENDARY", score
        elif score >= 45:
            return "RARE", score
        elif score >= 25:
            return "UNCOMMON", score
        else:
            return "COMMON", score

    def rarity_color(self, rarity):
        if rarity == "GOD":
            return Fore.RED + Style.BRIGHT
        elif rarity == "LEGENDARY":
            return Fore.YELLOW + Style.BRIGHT
        elif rarity == "RARE":
            return Fore.CYAN + Style.BRIGHT
        elif rarity == "UNCOMMON":
            return Fore.GREEN
        else:
            return Fore.WHITE

    def rarity_price(self, rarity):
        if rarity == "GOD":
            return "$500–$10,000+"
        elif rarity == "LEGENDARY":
            return "$100–$500"
        elif rarity == "RARE":
            return "$20–$100"
        elif rarity == "UNCOMMON":
            return "$5–$20"
        else:
            return "$1–$5"

    def save_result(self, username, rarity, score, sources):
        with open("free_usernames.txt", "a") as f:
            f.write(f"{username} | {rarity} ({score}) | {', '.join(sources)}\n")

    # ====== 1. SCAN ======
    def scan_forever(self, keywords, min_len=5, max_len=16, digits_allowed=True, use_affixes=True):
        self.found = []
        self.checked = 0
        start_time = time.time()

        self.log(f"Keywords: {', '.join(keywords)}", Fore.MAGENTA)
        self.log(f"Length: {min_len}-{max_len} | Digits: {'Yes' if digits_allowed else 'No'}", Fore.MAGENTA)
        self.log(f"Affixes: {'Yes' if use_affixes else 'No'}", Fore.MAGENTA)
        self.log("Generating usernames...", Fore.MAGENTA)

        usernames = self.generate_usernames(keywords, min_len, max_len, digits_allowed, use_affixes)
        self.log(f"Generated {len(usernames)} usernames. Scanning...", Fore.MAGENTA)
        self.log("Press Ctrl+C to stop.\n", Fore.YELLOW)

        try:
            for username in usernames:
                self.checked += 1

                tg = self.check_telegram(username)
                time.sleep(0.15)

                frag = self.check_fragment(username)
                time.sleep(0.15)

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
                self.log("FREE USERNAMES:", Fore.GREEN)
                for username, rarity, score, sources in sorted(self.found, key=lambda x: x[2], reverse=True)[:20]:
                    color = self.rarity_color(rarity)
                    self.log(f"  @{username} | {rarity} ({score}) | {', '.join(sources)}", color)

    # ====== 2. RATING ======
    def rating(self):
        print()
        username = input(Fore.WHITE + "Username (without @): ").strip().lower()
        if not username:
            return

        print(Fore.WHITE + "\n" + "=" * 40)
        print(Fore.WHITE + f"  RATING: @{username}")
        print(Fore.WHITE + "=" * 40)

        rarity, score = self.calculate_rarity(username)
        color = self.rarity_color(rarity)
        price = self.rarity_price(rarity)

        print(f"  Rarity:  {color}{rarity}{Style.RESET_ALL}")
        print(f"  Score:   {score}")
        print(f"  Length:  {len(username)}")
        print(f"  Digits:  {'Yes' if any(c.isdigit() for c in username) else 'No'}")
        print(f"  Price:   {price}")
        print(Fore.WHITE + "=" * 40)

    # ====== 3. VERIFY ======
    def verify(self):
        print()
        username = input(Fore.WHITE + "Username (without @): ").strip().lower()
        if not username:
            return

        print(Fore.WHITE + f"\n[*] Checking @{username}...")

        tg = self.check_telegram(username)
        time.sleep(0.3)
        frag = self.check_fragment(username)

        print(Fore.WHITE + "\n" + "=" * 40)
        print(Fore.WHITE + f"  VERIFY: @{username}")
        print(Fore.WHITE + "=" * 40)

        if tg == "free":
            print(Fore.GREEN + "  Telegram: FREE")
        elif tg == "taken":
            print(Fore.RED + "  Telegram: TAKEN")
        else:
            print(Fore.YELLOW + "  Telegram: UNKNOWN")

        if frag == "free":
            print(Fore.GREEN + "  Fragment: FREE")
        elif frag == "taken":
            print(Fore.RED + "  Fragment: TAKEN (or for sale)")
        else:
            print(Fore.YELLOW + "  Fragment: UNKNOWN")

        if tg == "free" and frag == "free":
            print(Fore.GREEN + "\n  RESULT: COMPLETELY FREE!")
        elif tg == "free" or frag == "free":
            print(Fore.YELLOW + "\n  RESULT: PARTIALLY FREE")
        else:
            print(Fore.RED + "\n  RESULT: TAKEN")

        print(Fore.WHITE + "=" * 40)

# ====== MAIN MENU ======
def main():
    print(Fore.CYAN + "=" * 40)
    print(Fore.CYAN + "   VACUUM v4.0")
    print(Fore.CYAN + "   Username Tool")
    print(Fore.CYAN + "=" * 40)

    scanner = UsernameScanner()

    while True:
        print()
        print(Fore.WHITE + "=" * 40)
        print(Fore.WHITE + "   MENU")
        print(Fore.WHITE + "=" * 40)
        print(Fore.WHITE + "  [1] Scan usernames")
        print(Fore.WHITE + "  [2] Username rating")
        print(Fore.WHITE + "  [3] Verify username")
        print(Fore.WHITE + "  [0] Exit")
        print(Fore.WHITE + "=" * 40)

        choice = input(Fore.WHITE + "\n> ").strip()

        if choice == '1':
            print()
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
            affixes = input("Add prefixes/suffixes? (y/n, default y): ").strip().lower() != 'n'

            print()
            scanner.scan_forever(keywords, min_len, max_len, digits, affixes)

        elif choice == '2':
            scanner.rating()

        elif choice == '3':
            scanner.verify()

        elif choice == '0':
            print(Fore.CYAN + "\nGoodbye!")
            break

        else:
            print(Fore.RED + "Wrong choice.")

if __name__ == "__main__":
    main()
