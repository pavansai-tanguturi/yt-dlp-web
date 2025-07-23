import random
import time
import hashlib

class StealthHelper:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15'
        ]
        self.ip_pool = []
        for _ in range(20):
            self.ip_pool.append({
                'ip': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'last_used': 0
            })
    
    def get_fresh_ip(self):
        current_time = time.time()
        available = [ip for ip in self.ip_pool if current_time - ip['last_used'] > 1800]
        if not available:
            available = self.ip_pool[:5]
        chosen = random.choice(available)
        chosen['last_used'] = current_time
        return chosen
    
    def get_realistic_timing(self, base=2.0, variance=3.0):
        return random.uniform(base, base + variance)
    
    def generate_session_fingerprint(self, url):
        timestamp = int(time.time())
        return hashlib.md5(f"{timestamp}{random.random()}{url}".encode()).hexdigest()[:12]
    
    def get_browser_entropy(self):
        return {
            'screen_width': random.choice(['1920', '1366', '1440']),
            'screen_height': random.choice(['1080', '768', '900']),
            'language': random.choice(['en-US', 'en-GB']),
            'platform': random.choice(['Win32', 'MacIntel'])
        }

stealth_helper = StealthHelper()
