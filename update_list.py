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
    # PUT để thay thế toàn bộ danh sách
    data = {"domains": domains}

    print(f"⏳ Đang gửi danh sách {list_type.upper()} ({len(domains)} domains) đến profile {profile_id}...")
    response = requests.put(url, json=data, headers=headers)

    print(f"Response code: {response.status_code}")
    print(f"Response body: {response.text}")

    if response.status_code == 200:
        print(f"✅ Đã thay thế {len(domains)} domain vào {list_type.upper()} của NextDNS profile {profile_id}!")
    else:
        print(f"❌ Lỗi {list_type.upper()}: {response.status_code} - {response.text}")

def get_nextdns_accounts():
    accounts = []
    index = 1
    while True:
        api_key = os.getenv(f"NEXTDNS_{index}_API_KEY")
        profile_id = os.getenv(f"NEXTDNS_{index}_PROFILE_ID")
        if not api_key or not profile_id:
            if index == 1:
                print("⚠️ Không tìm thấy biến môi trường NEXTDNS_1_API_KEY hoặc NEXTDNS_1_PROFILE_ID")
            break
        print(f"✅ Tìm thấy NEXTDNS_{index}_API_KEY và PROFILE_ID")
        accounts.append((api_key, profile_id))
        index += 1
    return accounts

if __name__ == "__main__":
    print("🚀 Bắt đầu cập nhật danh sách NextDNS...")

    blocklist_urls = get_list_urls("BLOCKLIST_URLS_")
    allowlist_urls = get_list_urls("ALLOWLIST_URLS_")

    accounts = get_nextdns_accounts()
    if not accounts:
        print("❗ Không có tài khoản NextDNS nào được cấu hình.")
        exit(1)

    if blocklist_urls:
        blocklist = fetch_domains(blocklist_urls)
        print(f"🌐 Tổng số domain trong Denylist: {len(blocklist)}")
    else:
        blocklist = []
        print("⚠️ Không có danh sách chặn (Denylist) nào được cung cấp.")

    if allowlist_urls:
        allowlist = fetch_domains(allowlist_urls)
        print(f"🌐 Tổng số domain trong Allowlist: {len(allowlist)}")
    else:
        allowlist = []
        print("⚠️ Không có danh sách cho phép (Allowlist) nào được cung cấp.")

    for api_key, profile_id in accounts:
        if blocklist:
            update_list(api_key, profile_id, blocklist, "denylist")
        if allowlist:
            update_list(api_key, profile_id, allowlist, "allowlist")

    print("🎉 Hoàn thành cập nhật danh sách NextDNS!")
