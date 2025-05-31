import os
import requests
import json

def get_env_var(key):
    return os.environ.get(key)

def fetch_domains_from_url(url):
    if not url or url.strip() == "":
        print(f"❌ Bỏ qua URL rỗng.")
        return []

    try:
        response = requests.get(url)
        response.raise_for_status()
        lines = response.text.splitlines()
        domains = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
        return domains
    except Exception as e:
        print(f"❌ Lỗi khi tải {url}\n: {e}")
        return []

def update_nextdns_list(api_key, profile_id, domains, list_type):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    batch_size = 1000
    for i in range(0, len(domains), batch_size):
        batch = domains[i:i+batch_size]

        # Tạo JSON object với id + domain
        data = [{"id": d, "domain": d} for d in batch]

        url = f"https://api.nextdns.io/profiles/{profile_id}/{list_type}"

        print(f"⏳ Gửi batch {list_type.upper()} {i}-{i+len(batch)-1} ({len(batch)} domains)")

        try:
            response = requests.put(url, headers=headers, data=json.dumps(data))
            if response.status_code in [200, 204]:
                print(f"✅ Batch {i}-{i+len(batch)-1} OK!")
            else:
                print(f"❌ Lỗi batch {list_type.upper()}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Lỗi batch {list_type.upper()}: {e}")

def update_nextdns_allowlist(api_key, profile_id, domains):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    url = f"https://api.nextdns.io/profiles/{profile_id}/allowlist"

    for domain in domains:
        data = {"id": domain, "domain": domain}

        print(f"⏳ Thêm ALLOWLIST: {domain}")
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code in [200, 201, 204]:
                print(f"✅ Thêm ALLOWLIST: {domain} OK!")
            else:
                print(f"❌ Lỗi ALLOWLIST: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Lỗi ALLOWLIST: {e}")

def main():
    print("\n🚀 Bắt đầu cập nhật danh sách NextDNS...\n")

    for idx in range(1, 10):
        api_key = get_env_var(f"NEXTDNS_{idx}_API_KEY")
        profile_id = get_env_var(f"NEXTDNS_{idx}_PROFILE_ID")
        if not api_key or not profile_id:
            continue

        print(f"✅ Tìm thấy NEXTDNS_{idx}_API_KEY và PROFILE_ID\n")

        # Fetch denylist domains
        denylist_urls = []
        for j in range(1, 10):
            url = get_env_var(f"BLOCKLIST_URLS_{j}")
            if url:
                denylist_urls.append(url)

        deny_domains = []
        for url in denylist_urls:
            print(f"🔗 Đang tải danh sách từ: {url}")
            deny_domains.extend(fetch_domains_from_url(url))

        print(f"\n🌐 Tổng số domain trong Denylist: {len(deny_domains)}\n")

        # Fetch allowlist domains
        allowlist_urls = []
        for j in range(1, 10):
            url = get_env_var(f"ALLOWLIST_URLS_{j}")
            if url:
                allowlist_urls.append(url)

        allow_domains = []
        for url in allowlist_urls:
            print(f"🔗 Đang tải danh sách từ: {url}")
            allow_domains.extend(fetch_domains_from_url(url))

        print(f"\n🌐 Tổng số domain trong Allowlist: {len(allow_domains)}\n")

        # Update NextDNS
        if deny_domains:
            update_nextdns_list(api_key, profile_id, deny_domains, "denylist")
        if allow_domains:
            update_nextdns_allowlist(api_key, profile_id, allow_domains)

    print("\n🎉 Hoàn thành cập nhật danh sách NextDNS!")

if __name__ == "__main__":
    main()
