import requests, names, random, string, time, os
from imapManager import get_finary_code

REFERRAL_CODE = "finary referral code here"
EMAIL_USER   = "test@gmail.com"
EMAIL_PASS   = "app password without blanks"  #App Password, NOT normal password!

class Finary():
    def __init__(self, taskNumber: int=0, totalTasks: int=1):
        print(f"[+] Initializing Signup Process... (Task {taskNumber}/{totalTasks})")
        self.session = requests.Session()
        self.fname = names.get_first_name()
        self.lname = names.get_last_name()
        def _random_dotted(domain, min_dots=1, max_dots=3):
            name, tld = domain.split('.', 1)
            positions = list(range(1, len(name)))
            if not positions:
                return domain
            num = random.randint(min_dots, min(max_dots, len(positions)))
            sel = sorted(random.sample(positions, num))
            parts = []
            last = 0
            for p in sel:
                parts.append(name[last:p])
                parts.append('.')
                last = p
            parts.append(name[last:])
            return ''.join(parts) + '.' + tld

        self.domain_variants = [_random_dotted(EMAIL_USER.split('@')[0]) for _ in range(5)]
        self.selected_domain = random.choice(self.domain_variants)
        self.email = f"{self.selected_domain}@gmail.com"
        self.password = self.generatePassword(random.randint(10, 12))
        r = self.initiateSignup()
        if r['response']['status'] == 'missing_requirements' and r['response']['object'] == 'sign_up_attempt':
            print(f"[+] Starting {self.email} registration")
            self.id = r['response']['id']
            r = self.sendOtp()
            if r['response']['verifications']['email_address']['object'] == 'verification_otp' and r['response']['verifications']['email_address']['status'] == 'unverified':
                print(f"[+] OTP code sent to {self.email}. Waiting for input...")
                print("[!] Waiting 10 seconds for the OTP to arrive in inbox...")
                time.sleep(10)
                otp = get_finary_code(
                    gmail_user=EMAIL_USER,
                    gmail_app_password=EMAIL_PASS,
                    from_addr="no-reply@email.finary.com",
                    to_addr=self.email,
                    unread_only=True
                )
                if not otp:
                    print("[-] Failed to retrieve OTP from email. Retrying in 10 seconds...")
                    time.sleep(10)
                    otp = get_finary_code(
                        gmail_user=EMAIL_USER,
                        gmail_app_password=EMAIL_PASS,
                        from_addr="no-reply@email.finary.com",
                        to_addr=self.email,
                        unread_only=True
                    )
                    if not otp:
                        print("[-] Failed to retrieve OTP from email again. Exiting.")
                        return
                print(f"[+] Verifying OTP...")
                r = self.verifyOtp(otp)
                if r['response']['status'] == 'complete':
                    print(f"[+] Account {self.email} successfully created! Proceeding to account linking...")
                    self.sessId = r['client']['last_active_session_id']
                    self.touch()
                    self.linkAccounts()
                    print(f"[+] Successfully linked accounts for {self.email}.")

    def generatePassword(self, length=10):
        upper = random.choice(string.ascii_uppercase)
        digit = random.choice(string.digits)
        special = random.choice("!@#$%^&*()-_=+[]{}")

        pool = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}"
        remaining = "".join(random.choice(pool) for _ in range(length - 3))

        pwd_list = list(upper + digit + special + remaining)
        random.shuffle(pwd_list)

        return "".join(pwd_list)

    def initiateSignup(self):
        headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'dnt': '1',
            'origin': 'https://app.finary.com',
            'priority': 'u=1, i',
            'referer': 'https://app.finary.com/',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        }

        params = {
            '__clerk_api_version': '2025-04-10',
            '_clerk_js_version': '5.103.1',
        }

        data = {
            'email_address': self.email,
            'password': self.password,
            'unsafe_metadata': '{"firstname":"' + self.fname + '","lastname":"' + self.lname + '","country":"FR","godfather_referral_id":"' + REFERRAL_CODE + '","signup_source":"friends","registration_platform":"web_app","display_language":"en","display_currency":"EUR"}',
            'locale': 'en-GB',
        }

        response = self.session.post(
            'https://clerk.finary.com/v1/client/sign_ups', 
            params=params, 
            headers=headers, 
            data=data
        )

        if response.status_code == 200:
            return response.json()
        
    def sendOtp(self):
        headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'dnt': '1',
            'origin': 'https://app.finary.com',
            'priority': 'u=1, i',
            'referer': 'https://app.finary.com/',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        }

        params = {
            '__clerk_api_version': '2025-04-10',
            '_clerk_js_version': '5.103.1',
        }

        data = {
            'strategy': 'email_code',
        }

        response = self.session.post(
            f'https://clerk.finary.com/v1/client/sign_ups/{self.id}/prepare_verification',
            params=params,
            headers=headers,
            data=data,
        )

        if response.status_code == 200:
            return response.json()
        
    
    def verifyOtp(self, otp):
        headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'dnt': '1',
            'origin': 'https://app.finary.com',
            'priority': 'u=1, i',
            'referer': 'https://app.finary.com/',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        }

        params = {
            '__clerk_api_version': '2025-04-10',
            '_clerk_js_version': '5.103.1',
        }

        data = {
            'strategy': 'email_code',
            'code': otp,
        }

        response = self.session.post(
            f'https://clerk.finary.com/v1/client/sign_ups/{self.id}/attempt_verification',
            params=params,
            headers=headers,
            data=data,
        )
        if response.status_code == 200:
            return response.json()
        
    
    def touch(self):
        headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'dnt': '1',
            'origin': 'https://app.finary.com',
            'priority': 'u=1, i',
            'referer': 'https://app.finary.com/',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        }

        params = {
            '__clerk_api_version': '2025-04-10',
            '_clerk_js_version': '5.103.1',
        }

        data = {
            'active_organization_id': '',
        }

        response = self.session.post(
            f'https://clerk.finary.com/v1/client/sessions/{self.sessId}/touch',
            params=params,
            headers=headers,
            data=data,
        )
        if response.status_code == 200:
            return response.json()
        
    
    def linkAccounts(self):
        headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'dnt': '1',
            'origin': 'https://app.finary.com',
            'priority': 'u=1, i',
            'referer': 'https://app.finary.com/',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        }

        params = {
            '__clerk_api_version': '2025-04-10',
            '_clerk_js_version': '5.103.1',
        }

        data = {
            'organization_id': '',
        }

        response = self.session.post(
            f'https://clerk.finary.com/v1/client/sessions/{self.sessId}/tokens',
            params=params,
            headers=headers,
            data=data,
        )
        if response.status_code == 200:
            jwt = response.json()['jwt']

        headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en;q=0.9',
            'authorization': f'Bearer {jwt}',
            'dnt': '1',
            'origin': 'https://app.finary.com',
            'priority': 'u=1, i',
            'referer': 'https://app.finary.com/',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'x-client-api-version': '2',
            'x-finary-client-id': 'webapp',
        }

        response = self.session.get('https://api.finary.com/users/me/organizations', headers=headers)
        org_id = response.json()['result'][0]['id']
        fam_id = response.json()['result'][0]['members'][0]['id']
        
        headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en;q=0.9',
            'authorization': f'Bearer {jwt}',
            'content-type': 'application/json',
            'dnt': '1',
            'origin': 'https://app.finary.com',
            'priority': 'u=1, i',
            'referer': 'https://app.finary.com/',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'traceparent': '00-000000000000000041b7128fe93e03e6-41fbf6b1392bfcb3-01',
            'tracestate': 'dd=s:1;o:rum',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'x-client-api-version': '2',
            'x-datadog-origin': 'rum',
            'x-datadog-parent-id': '4754665072648518835',
            'x-datadog-sampling-priority': '1',
            'x-datadog-trace-id': '4735273942506144742',
            'x-finary-client-id': 'webapp',
        }

        json_data = {
            'name': 'Solana Wallet',
            'address': 'EnxFkSMoJkEzYUkWHubEXYKw2y9HQVUEHGmXrMyQniKu',
            'ownership_repartition': [
                {
                    'membership_id': fam_id,
                    'share': 1,
                },
            ],
            'exchange': 'solana',
        }

        response = self.session.post(
            f'https://api.finary.com/organizations/{org_id}/memberships/{fam_id}/crypto_accounts',
            headers=headers,
            json=json_data,
        )

        json_data = {
            'name': 'Solana Wallet',
            'address': 'FzZ77TM8Ekcb6gyWPmcT9upWkAZKZc5xrYfuFu7pifPn',
            'ownership_repartition': [
                {
                    'membership_id': fam_id,
                    'share': 1,
                },
            ],
            'exchange': 'solana',
        }

        response = self.session.post(
            f'https://api.finary.com/organizations/{org_id}/memberships/{fam_id}/crypto_accounts',
            headers=headers,
            json=json_data,
        )

if __name__ == '__main__':
    print('''
     ______ _                           _____            
    |  ____(_)                         / ____|           
    | |__   _ _ __   __ _ _ __ _   _  | |  __  ___ _ __  
    |  __| | | '_ \ / _` | '__| | | | | | |_ |/ _ \ '_ \ 
    | |    | | | | | (_| | |  | |_| | | |__| |  __/ | | |
    |_|    |_|_| |_|\__,_|_|   \__, |  \_____|\___|_| |_|
                                __/ |                    
                               |___/                     

    By @mati.smrd / Star the project if you found it useful!
          
    ''')
    qty = int(input('    How many accounts do you want to create? '))

    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    clear_console()

    for i in range(qty):
        Finary(taskNumber=i+1, totalTasks=qty)
    print("[!] All accounts generated! Don't forget to star the project !")


