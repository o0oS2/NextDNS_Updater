import requests
import os

def get_list_urls(prefix):
    urls = []
    for key, value in os.environ.items():
        if key.startswith(prefix):
            urls.append(value)
    return urls

def fetch_domains(urls):
    domains = set()
    for url in urls:
        print(f"🔗 Đang tải danh sách từ: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            for line in response.text.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    domains.add(line)
        else:
            print(f"❌ Lỗi khi tải {url}: {response.status_code}")
    return sorted(domains)

def update_list(api_key, profile_id, domains, list_type):
    url = f"https://api.nextdns.io/profiles/{profile_id}/{list_type}"
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    data = {"add": domains}

    response = requests.patch(url, json=data, headers=headers)
    if response.status_code == 200:
        print(f"✅ Đã cập nhật {len(domains)} domain vào {list_type.upper()} của NextDNS {profile_id}!")
    else:
        print(f"❌ Lỗi {list_type.upper()}: {response.status_code} - {response.text}")

def get_nextdns_accounts():
    accounts = []
    index = 1
    while True:
        api_key = os.getenv(f"NEXTDNS_{index}_API_KEY")
        profile_id = os.getenv(f"NEXTDNS_{index}_PROFILE_ID")
        if not api_key or not profile_id:
            break
        accounts.append((api_key, profile_id))
        index += 1
    return accounts

if __name__ == "__main__":
    blocklist_urls = get_list_urls("BLOCKLIST_URLS_")
    allowlist_urls = get_list_urls("ALLOWLIST_URLS_")

    accounts = get_nextdns_accounts()
    if not accounts:
        print("❗ Không tìm thấy biến NEXTDNS_x_API_KEY và NEXTDNS_x_PROFILE_ID trong Secrets.")
        exit(1)

    if blocklist_urls:
        blocklist = fetch_domains(blocklist_urls)
        print(f"🌐 Tổng số domain sẽ chặn (Denylist): {len(blocklist)}")
    else:
        blocklist = []

    if allowlist_urls:
        allowlist = fetch_domains(allowlist_urls)
        print(f"🌐 Tổng số domain cho phép (Allowlist): {len(allowlist)}")
    else:
        allowlist = []

    for api_key, profile_id in accounts:
        if blocklist:
            update_list(api_key, profile_id, blocklist, "denylist")
        if allowlist:
            update_list(api_key, profile_id, allowlist, "allowlist")
