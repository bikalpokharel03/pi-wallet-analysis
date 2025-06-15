import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class PiNetworkAnalyzer:
    def __init__(self):
        self.api_url = os.getenv("PI_API_URL")
        self.wallet = os.getenv("WALLET_ADDRESS")

    def get_claimable_balances(self):
        """Fetch claimable balances for your wallet"""
        url = f"{self.api_url}/accounts/{self.wallet}/claimable_balances"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()["_embedded"]["records"]
        except Exception as e:
            print(f"🚨 Error: {e}")
            return []

    def analyze_balance(self, balance):
        """Check if balance is claimable"""
        created_at = datetime.fromisoformat(balance["created_at"].replace("Z", "+00:00"))
        now = datetime.utcnow()

        for claimant in balance["claimants"]:
            if claimant["destination"] == self.wallet:
                if "not" in claimant["predicate"] and "rel_before" in claimant["predicate"]["not"]:
                    max_wait = int(claimant["predicate"]["not"]["rel_before"])
                    deadline = created_at + timedelta(seconds=max_wait)
                    return {
                        "amount": balance["amount"],
                        "deadline": deadline,
                        "can_claim": now < deadline,
                        "time_left": deadline - now if now < deadline else "EXPIRED"
                    }
        return None

if __name__ == "__main__":
    analyzer = PiNetworkAnalyzer()
    print(f"\n🔍 Analyzing Pi Wallet: {analyzer.wallet}")

    balances = analyzer.get_claimable_balances()
    if balances:
        print(f"💰 Found {len(balances)} claimable balances:")
        for balance in balances:
            result = analyzer.analyze_balance(balance)
            if result:
                print(f"\n💵 Amount: {result['amount']} π")
                print(f"⏳ Deadline: {result['deadline']}")
                print(f"🔄 Can claim now: {'✅ YES' if result['can_claim'] else '❌ NO'}")
                print(f"⏱️ Time left: {result['time_left']}")
    else:
        print("❌ No claimable balances found.")