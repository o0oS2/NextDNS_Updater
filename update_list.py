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
        try:
            response = requests.get(url)
            response.raise_for_status()
            for line in response.text.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    domains.add(line)
        except Exception as e:
            print(f"❌ Lỗi khi tải {url}: {e}")
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
            print(f"⚠️ Không tìm thấy NEXTDNS_{index}_API_KEY hoặc NEXTDNS_{index}_PROFILE_ID - Kiểm tra tên biến trong Secrets!")
            break
        print(f"✅ Tìm thấy API_KEY và PROFILE_ID cho index {index}")
        accounts.append((api_key, profile_id))
        index += 1
    return accounts

if __name__ == "__main__":
    print("🚀 Bắt đầu cập nhật danh sách NextDNS...")

    blocklist_urls = get_list_urls("BLOCKLIST_URLS_")
    allowlist_urls = get_list_urls("ALLOWLIST_URLS_")

    accounts = get_nextdns_accounts()
    if not accounts:
        print("❗ Không tìm thấy cặp biến NEXTDNS_x_API_KEY và NEXTDNS_x_PROFILE_ID trong Secrets.")
        exit(1)

    if blocklist_urls:
        blocklist = fetch_domains(blocklist_urls)
        print(f"🌐 Tổng số domain sẽ chặn (Denylist): {len(blocklist)}")
    else:
        blocklist = []
        print("⚠️ Không tìm thấy danh sách chặn (BLOCKLIST_URLS_x) nào.")

    if allowlist_urls:
        allowlist = fetch_domains(allowlist_urls)
        print(f"🌐 Tổng số domain cho phép (Allowlist): {len(allowlist)}")
    else:
        allowlist = []
        print("⚠️ Không tìm thấy danh sách cho phép (ALLOWLIST_URLS_x) nào.")

    for api_key, profile_id in accounts:
        if blocklist:
            update_list(api_key, profile_id, blocklist, "denylist")
        if allowlist:
            update_list(api_key, profile_id, allowlist, "allowlist")

    print("🎉 Hoàn thành cập nhật danh sách NextDNS!")
