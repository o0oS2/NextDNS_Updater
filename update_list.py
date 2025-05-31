import os
import requests
import json

def load_domains_from_urls(urls):
    domains = set()
    for url in urls:
        url = url.strip()
        if not url:
            print(f"❌ Bỏ qua URL rỗng.")
            continue
        print(f"🔗 Đang tải danh sách từ: {url}")
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            lines = response.text.splitlines()
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    domains.add(line)
        except Exception as e:
            print(f"❌ Lỗi khi tải {url}\n: {e}")
    return list(domains)

def update_nextdns_list(api_key, profile_id, endpoint, domains):
    if not domains:
        print(f"⚠️ Không có domain nào để cập nhật {endpoint}. Bỏ qua...")
        return

    url = f"https://api.nextdns.io/profiles/{profile_id}/{endpoint}"
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }

    payload = {"domain": domains}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"Response code: {response.status_code}")
        print(f"Response body: {response.text}")
        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Cập nhật {endpoint} thành công ({len(domains)} domains)")
        else:
            print(f"❌ Lỗi khi cập nhật {endpoint}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Lỗi khi gửi API: {e}")

def main():
    print("🚀 Bắt đầu cập nhật danh sách NextDNS...")

    accounts = []
    for i in range(1, 10):
        api_key = os.environ.get(f'NEXTDNS_{i}_API_KEY', '').strip()
        profile_id = os.environ.get(f'NEXTDNS_{i}_PROFILE_ID', '').strip()
        if api_key and profile_id:
            print(f"✅ Tìm thấy NEXTDNS_{i}_API_KEY và PROFILE_ID")
            accounts.append((api_key, profile_id))
        else:
            continue

    # Load blocklist và allowlist
    blocklist_urls = []
    for i in range(1, 10):
        url = os.environ.get(f'BLOCKLIST_URLS_{i}', '').strip()
        if url:
            blocklist_urls.append(url)

    allowlist_urls = []
    for i in range(1, 10):
        url = os.environ.get(f'ALLOWLIST_URLS_{i}', '').strip()
        if url:
            allowlist_urls.append(url)

    blocklist_domains = load_domains_from_urls(blocklist_urls)
    print(f"🌐 Tổng số domain trong Denylist: {len(blocklist_domains)}")

    allowlist_domains = load_domains_from_urls(allowlist_urls)
    print(f"🌐 Tổng số domain trong Allowlist: {len(allowlist_domains)}")

    for api_key, profile_id in accounts:
        print(f"⏳ Đang gửi danh sách DENYLIST ({len(blocklist_domains)} domains) đến profile {profile_id}...")
        update_nextdns_list(api_key, profile_id, 'denylist', blocklist_domains)

        print(f"⏳ Đang gửi danh sách ALLOWLIST ({len(allowlist_domains)} domains) đến profile {profile_id}...")
        update_nextdns_list(api_key, profile_id, 'allowlist', allowlist_domains)

    print("🎉 Hoàn thành cập nhật danh sách NextDNS!")

if __name__ == "__main__":
    main()
