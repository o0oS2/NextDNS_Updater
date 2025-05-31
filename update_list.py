import os
import requests
import json
import time

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

def send_denylist(api_key, profile_id, domains, batch_size=1000):
    url = f"https://api.nextdns.io/profiles/{profile_id}/denylist"
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }

    for i in range(0, len(domains), batch_size):
        batch = domains[i:i+batch_size]
        payload = {"domain": batch}
        print(f"⏳ Gửi batch DENYLIST {i}-{i+len(batch)-1} ({len(batch)} domains)")
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            print(f"Response code: {response.status_code}")
            print(f"Response body: {response.text}")
            if response.status_code in [200, 201]:
                print(f"✅ Batch DENYLIST thành công.")
            else:
                print(f"❌ Lỗi batch DENYLIST: {response.status_code} - {response.text}")
            time.sleep(1)  # Giảm tải API
        except Exception as e:
            print(f"❌ Lỗi khi gửi batch DENYLIST: {e}")

def send_allowlist(api_key, profile_id, domains):
    url = f"https://api.nextdns.io/profiles/{profile_id}/allowlist"
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }

    for domain in domains:
        payload = {"id": domain}
        print(f"⏳ Thêm ALLOWLIST: {domain}")
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            print(f"Response code: {response.status_code}")
            print(f"Response body: {response.text}")
            if response.status_code in [200, 201]:
                print(f"✅ ALLOWLIST thành công: {domain}")
            else:
                print(f"❌ Lỗi ALLOWLIST: {response.status_code} - {response.text}")
            time.sleep(0.5)
        except Exception as e:
            print(f"❌ Lỗi ALLOWLIST {domain}: {e}")

def main():
    print("🚀 Bắt đầu cập nhật danh sách NextDNS...")

    accounts = []
    for i in range(1, 10):
        api_key = os.environ.get(f'NEXTDNS_{i}_API_KEY', '').strip()
        profile_id = os.environ.get(f'NEXTDNS_{i}_PROFILE_ID', '').strip()
        if api_key and profile_id:
            print(f"✅ Tìm thấy NEXTDNS_{i}_API_KEY và PROFILE_ID")
            accounts.append((api_key, profile_id))

    blocklist_urls = [os.environ.get(f'BLOCKLIST_URLS_{i}', '').strip() for i in range(1, 10)]
    allowlist_urls = [os.environ.get(f'ALLOWLIST_URLS_{i}', '').strip() for i in range(1, 10)]

    blocklist_domains = load_domains_from_urls(blocklist_urls)
    print(f"🌐 Tổng số domain trong Denylist: {len(blocklist_domains)}")

    allowlist_domains = load_domains_from_urls(allowlist_urls)
    print(f"🌐 Tổng số domain trong Allowlist: {len(allowlist_domains)}")

    for api_key, profile_id in accounts:
        print(f"⏳ Đang gửi danh sách DENYLIST ({len(blocklist_domains)} domains) đến profile {profile_id}...")
        send_denylist(api_key, profile_id, blocklist_domains)

        print(f"⏳ Đang gửi danh sách ALLOWLIST ({len(allowlist_domains)} domains) đến profile {profile_id}...")
        send_allowlist(api_key, profile_id, allowlist_domains)

    print("🎉 Hoàn thành cập nhật danh sách NextDNS!")

if __name__ == "__main__":
    main()
