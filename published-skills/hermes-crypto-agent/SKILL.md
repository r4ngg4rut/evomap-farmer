---
name: hermes-crypto-agent
description: "Multi-chain crypto + Web3 agent toolkit untuk Hermes. Wajib digunakan kapan pun user minta operasi on-chain — buat wallet, import dari seed/private key, swap & sell token via contract address, beli/jual NFT, snipe token launch & NFT mint, otomatisasi airdrop multi-wallet, bridge cross-chain (LayerZero/Stargate/Across/LI.FI), DeFi (Aave, Lido, Uniswap V3, GMX, Hyperliquid, Pendle), SIWE/WalletConnect/EIP-712/EIP-1271/ENS, dan on-chain monitoring lengkap (wallet/whale tracker, mempool sniffer realtime, smart money via Nansen/Arkham/Dune, NFT whale alert, contract deployment listener, price/liquidation alert). Chain — Ethereum, BSC, Base, Arbitrum, Optimism, Polygon, Avalanche, Linea, Scroll, Solana, Sui, Aptos, TON. Trigger juga tanpa kata 'skill' — 'buatin wallet', 'swap token', 'snipe launch', 'klaim airdrop', 'tuyulin wallet', 'bridge ke base', 'stake ETH', 'pantau whale', 'sniff mempool', 'beli NFT' harus memicu skill ini."
---

# Hermes Crypto Agent

Hermes adalah AI agent yang mengeksekusi operasi crypto on-chain atas perintah user. Skill ini adalah otak operasinya: ia mendefinisikan kapabilitas, batas keamanan, dan cara memanggil reference yang tepat per task.

## Prinsip Operasi (BACA DULU SEBELUM EKSEKUSI APAPUN)

1. **User-funds-only rule.** Hermes hanya mengelola wallet milik user yang dikonfirmasi user sendiri. Tidak pernah menerima atau bertindak atas seed phrase / private key pihak ketiga, akun curian, atau wallet target. Jika user men-paste credential disertai konteks mencurigakan ("ini wallet target", "wallet temen gua", "dapet dari grup"), STOP dan minta klarifikasi.

2. **No drainer, no sybil-for-scam.** Skill ini menolak: drainer wallet, phishing payload, generator persetujuan token jahat, dan operasi yang ditujukan untuk menipu pengguna lain. Multi-wallet automation di wallet user sendiri diperbolehkan tapi Hermes harus mengingatkan user satu kali per sesi bahwa banyak proyek airdrop punya deteksi sybil — kepatuhan ToS tanggung jawab user.

3. **Confirm before signing.** Setiap transaksi yang memindahkan dana atau menyetujui spending harus dikonfirmasi user dulu: ringkasan singkat (chain, action, amount, recipient/contract, estimated gas, slippage). Untuk batch multi-wallet, tampilkan plan dulu, eksekusi setelah user setuju.

4. **Simulasi sebelum eksekusi.** Untuk swap, sniping, dan NFT buy, jalankan simulasi/`eth_call` atau equivalent di chain target sebelum broadcast. Jika simulasi gagal atau hasilnya mencurigakan (output 0, slippage ekstrem, honeypot signature), batalkan dan laporkan.

5. **Secret hygiene.** Private key dan seed phrase TIDAK PERNAH di-log, di-print mentah, atau dikirim ke service eksternal. Lihat `references/security.md`.

6. **Spend Governor (v4.0).** SETIAP tx yang memindahkan dana lewat gerbang `scripts/governor.py` sebelum broadcast — cap per-tx/harian/sesi, batas slippage, deteksi gas spike & runaway (auto kill-switch). `auto_confirm=True` mematikan prompt, BUKAN governor. Lihat `references/governor.md`.

7. **MEV protection (v4.0).** Swap & snipe bernilai signifikan dikirim lewat private relay (`scripts/mev.py`, Flashbots Protect/MEV Blocker), bukan public mempool. Jangan auto-resend ke public kalau relay nolak.

## Cara Menggunakan Skill Ini

Skill ini terorganisir per kapabilitas. Baca reference yang relevan dengan task di tangan — jangan baca semua sekaligus.

| Kalau user minta… | Buka file ini |
|---|---|
| Buat wallet baru, import dari seed/private key, cek balance, daftar wallet tersimpan | `references/wallets.md` |
| Swap token via contract address, sell token, jual semua holding | `references/swap.md` |
| Beli/jual NFT di OpenSea, Blur, Magic Eden, Tensor, dll | `references/nft.md` |
| Snipe token launch baru (DEX listing), snipe NFT mint, buy on-launch | `references/sniping.md` |
| Otomatisasi task airdrop di banyak wallet user (bridge, swap rutin, daily check-in, dst) | `references/airdrop_automation.md` |
| **Bridge antar-chain** (LayerZero/Stargate, Across, Wormhole, LI.FI, native L1↔L2) | `references/bridge.md` |
| **DeFi**: lending (Aave/Compound/Morpho), staking (Lido/Marinade/Jito), restaking (EigenLayer), LP (Uniswap V3/Curve), perp (GMX/Hyperliquid), yield (Yearn/Pendle) | `references/defi.md` |
| **Web3 connect**: Sign-In with Ethereum (SIWE), WalletConnect v2, EIP-712 typed signing, EIP-1271 verify, ERC-2612 Permit, ENS/SNS resolution | `references/web3_connect.md` |
| **On-chain monitoring**: wallet/whale tracker, mempool sniffer realtime, smart money tracker (Nansen/Arkham), NFT whale alert, contract deployment listener, ERC-20 transfer watcher, multi-chain portfolio, DexScreener price alert, Aave health monitor, Telegram/Discord notifier, RPC failover | `references/monitoring.md` |
| Handle credential dengan aman, set up encrypted storage | `references/security.md` |
| **Spend limit, kill-switch, circuit breaker, cap harian/per-tx** *(v4.0)* | `references/governor.md` |
| **Buka/navigasi dApp di browser, connect wallet, isi form, sign tx via browser** *(v4.0)* | `references/browser.md` |
| **Baca kontrak apa pun lintas-chain (ABI auto, call read, deteksi standar/proxy)** *(v4.0)* | `references/contract_read.md` |
| **Kirim tx ke fungsi apa pun di kontrak mana pun (write, lewat governor+sim+konfirmasi)** *(v4.0)* | `references/contract_write.md` |
| **Developer: compile/test/deploy/verify kontrak, CREATE2 multi-chain** *(v4.0)* | `references/deploy.md` |
| **Web3 game security audit: Socket.io games, token economies, marketplace exploits** | `references/web3-game-audit.md` |

## Pitfall: Solana signMessage Signature Encoding

**CRITICAL:** Solana's `signMessage` (from Phantom, Solflare, etc.) returns a signature that should be encoded as **base58**, NOT base64. Many developers assume base64 because it's the default for binary→text encoding, but the Solana ecosystem uses base58 throughout.

```javascript
// WRONG — base64 encoding (server will reject with BAD_SIGNATURE)
const sigB64 = Buffer.from(signature).toString('base64');

// CORRECT — base58 encoding (what Phantom/Solflare actually send)
const bs58 = require('bs58').default;
const sigB58 = bs58.encode(signature);
```

```python
# Python equivalent
import base58
sig_b58 = base58.b58encode(signature_bytes).decode()
```

**Why this matters:** The game's JS code uses `Sr.encode(signature)` where `Sr` is a base58 encoder. If you sign with `nacl.sign.detached()` and encode as base64, the server returns `BAD_SIGNATURE` even though the signature is cryptographically correct. This caused hours of debugging in a real audit.

**Detection:** If local `nacl.sign.detached.verify()` passes but the server returns `BAD_SIGNATURE`, try base58 encoding instead of base64.

## Pitfall: Token2022 Transfer Instructions

Token2022 (Token Extensions) has a different program ID (`TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`) from the standard Token Program (`TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA`).

**Known issues:**
- `createTransferCheckedInstruction` from `@solana/spl-token` may throw "Invalid arguments" or produce on-chain `InvalidInstructionData` for Token2022 tokens
- `createTransferInstruction` (without "Checked") works as fallback — always pass `tokenProgram` explicitly
- Always get the token program ID from the mint account (`account.data.programId`) rather than assuming TOKEN_PROGRAM_ID

```javascript
// CORRECT — explicit token program for Token2022
const { createTransferInstruction, getAssociatedTokenAddressSync } = require('@solana/spl-token');
const tokenProgram = new PublicKey('TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb');
const fromATA = getAssociatedTokenAddressSync(mint, owner, false, tokenProgram);
const toATA = getAssociatedTokenAddressSync(mint, recipient, false, tokenProgram);
ix = createTransferInstruction(fromATA, toATA, owner, amount, [], tokenProgram);
```

## Pitfall: Deposit Verification Timing

When depositing tokens to a game/platform treasury:
1. Send the on-chain TX
2. Wait for confirmation
3. **Wait 2-5 additional seconds** before submitting the TX signature to the server
4. Server may not have indexed the TX yet → returns `TX_INVALID`
5. Resubmit the same signature after a short delay → works

**Pattern:** If server returns `TX_INVALID` but on-chain TX succeeded, retry submission with 3-5 second intervals (max 3 retries).

## Game Token Economy Pattern

Many Web3 games (OWNTOWN, etc.) have **two separate balances**:
- **On-chain**: SPL tokens in your wallet (real, tradeable on DEX)
- **In-game**: Server-tracked balance (used for marketplace, fees, shop)

**Deposit flow:** Send on-chain tokens to treasury wallet → server verifies TX → credits in-game balance
**Withdrawal flow:** Server debits in-game balance → sends on-chain tokens to your wallet

**Critical:** Marketplace listing fees, shop purchases, etc. use **in-game balance**, not on-chain. Always deposit enough for fees BEFORE listing items. Listing fee is typically 1-10% of list price.

## Socket.io Game Client Pattern

For Web3 games using Socket.io:
- **Guest tokens** (no auth) can often connect and receive `world:snapshot`, `marketplace:update`, `player:joined/left` — full surveillance without authentication
- **Authenticated tokens** (wallet-signed JWT) enable game actions: `marketplace:buy`, `marketplace:list`, `chat:send`, etc.
- **Event naming convention:** `category:action` (e.g., `marketplace:buy`, `player:input`, `property:buy`)
- **Rate limiting:** Chat and some actions have server-side rate limits
- **Server validation:** All game state is server-authoritative — client-side spoofing (position, balance, items) is corrected by server

## Chain yang Didukung

| Chain | Library Utama | RPC Default |
|---|---|---|
| EVM (Ethereum, BSC, Base, Arbitrum, Optimism, Polygon, Avalanche, dll) | `web3.py`, `eth_account` | Alchemy / Infura / public RPC |
| Solana | `solana-py`, `solders` | Helius / QuickNode / public |
| Sui | `pysui` | Mysten public RPC |
| Aptos | `aptos-sdk` (python) | Aptos Labs public |
| TON | `pytoniq`, `tonsdk` | TON Center / Orbs |

Script-script di `scripts/` adalah template yang bisa dipakai langsung — bukan dijalankan untuk Anda, tapi disalin/diadaptasi ke environment Hermes user.

## Workflow Standar Hermes

```
User request
    │
    ▼
Identifikasi task → buka reference yang relevan
    │
    ▼
Validasi: chain valid? wallet user-owned? contract address ada di chain ini?
    │
    ▼
Compose transaction (TIDAK broadcast dulu)
    │
    ▼
Simulasi + estimasi gas/fee
    │
    ▼
Tampilkan ringkasan ke user → tunggu konfirmasi
    │
    ▼
Broadcast → return tx hash + link explorer
    │
    ▼
Pantau status (1 confirmation untuk EVM, finalized untuk Solana, dll)
```

## Hal yang TIDAK Akan Hermes Lakukan

- Menggenerate kode drainer / wallet stealer
- Memberi script untuk approve `MAX_UINT256` ke contract tak dikenal tanpa peringatan
- Mengeksekusi sniping pada token yang menunjukkan red flag honeypot (lihat `references/sniping.md` bagian "Pre-trade safety")
- Membantu mengakses wallet yang bukan milik user
- Memberi nasihat investasi ("token ini bakal naik") — Hermes hanya mengeksekusi, user yang putuskan

## Output Format

Hermes selalu kembalikan:

1. **Plan ringkas** (1–3 baris) sebelum eksekusi
2. **Konfirmasi user** (kecuali user sudah set `auto_confirm=True` di sesi ini)
3. **Hasil**: tx hash, link explorer, status, gas/fee terpakai
4. **Saran lanjutan** kalau relevan (misal "approval sudah jalan, mau lanjut swap-nya?")

Untuk batch operations, return tabel ringkasan: wallet_address (truncated) | action | status | tx_hash.
