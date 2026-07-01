#!/usr/bin/env python3
"""
Publish all 75 distilled skills to EvoMap Hub via A2A protocol.
"""
import json, os, time, sys, hashlib
from pathlib import Path
import urllib.request

SKILLS_DIR = Path.home() / 'evomap-farmer' / 'published-skills'
NODE_SECRET = open(Path.home() / '.evomap' / 'node_secret').read().strip()
NODE_ID = open(Path.home() / '.evomap' / 'node_id').read().strip()
HUB_URL = 'https://evomap.ai'

PUBLISHED_LOG = SKILLS_DIR / 'published.log'

def publish_asset(gene, capsule):
    """Publish Gene + Capsule bundle via A2A API"""
    url = f"{HUB_URL}/a2a/publish"
    
    # A2A message format
    message = {
        "type": "a2a_message",
        "protocol_version": "1.0",
        "sender_id": NODE_ID,
        "message_type": "publish",
        "payload": {
            "assets": [gene, capsule],
            "node_id": NODE_ID
        }
    }
    
    body = json.dumps(message).encode()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {NODE_SECRET}',
        'X-Node-Id': NODE_ID,
        'X-Node-Secret': NODE_SECRET
    }
    
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                response = json.loads(resp.read())
                return True, response
        except urllib.error.HTTPError as e:
            if e.code == 429:
                retry_after = int(e.headers.get('Retry-After', 5))
                print(f"  ⏳ Rate limited, waiting {retry_after}s...")
                time.sleep(retry_after + 1)
                continue
            elif e.code == 409:
                return False, {"status": "duplicate", "code": 409}
            else:
                body_text = e.read().decode()
                return False, {"status": "error", "code": e.code, "body": body_text[:500]}
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return False, {"status": "exception", "error": str(e)}

def compute_asset_id(data):
    """Compute SHA256 content hash for asset_id"""
    # Canonical JSON (sorted keys)
    canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return 'sha256:' + hashlib.sha256(canonical.encode()).hexdigest()

def main():
    # Load previously published
    published = set()
    if PUBLISHED_LOG.exists():
        for line in PUBLISHED_LOG.read_text().strip().split('\n'):
            if line:
                published.add(line.strip())
    
    # Get all skill directories
    skill_dirs = sorted([d for d in SKILLS_DIR.iterdir() if d.is_dir()])
    print(f"Found {len(skill_dirs)} skills to publish")
    
    published_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, skill_dir in enumerate(skill_dirs):
        name = skill_dir.name
        
        if name in published:
            skipped_count += 1
            continue
        
        gene_file = skill_dir / 'gene.json'
        capsule_file = skill_dir / 'capsule.json'
        
        if not gene_file.exists() or not capsule_file.exists():
            print(f"  ⏭️ {name}: missing files")
            skipped_count += 1
            continue
        
        gene = json.loads(gene_file.read_text())
        capsule = json.loads(capsule_file.read_text())
        
        # Compute asset_ids
        gene['asset_id'] = compute_asset_id(gene)
        capsule['asset_id'] = compute_asset_id(capsule)
        
        print(f"  [{i+1}/{len(skill_dirs)}] Publishing {name}...", end=' ')
        sys.stdout.flush()
        
        ok, result = publish_asset(gene, capsule)
        
        if ok:
            print(f"✅")
            published_count += 1
            with open(PUBLISHED_LOG, 'a') as f:
                f.write(f"{name}\n")
        else:
            status = result.get('status', 'unknown')
            if status == 'duplicate' or result.get('code') == 409:
                print(f"⏭️ (already exists)")
                skipped_count += 1
                with open(PUBLISHED_LOG, 'a') as f:
                    f.write(f"{name}\n")
            else:
                print(f"❌ {status}: {result.get('body', result.get('error', 'unknown'))[:100]}")
                error_count += 1
        
        # Rate limit: 10/min free tier, so 6s between
        if (i + 1) % 10 == 0:
            print(f"  --- Rate limit pause ---")
            time.sleep(10)
        else:
            time.sleep(6)
    
    print(f"\n{'='*50}")
    print(f"✅ Published: {published_count}")
    print(f"⏭️ Skipped: {skipped_count}")
    print(f"❌ Errors: {error_count}")
    print(f"Total: {len(skill_dirs)}")

if __name__ == '__main__':
    main()