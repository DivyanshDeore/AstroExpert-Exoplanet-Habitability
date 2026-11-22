def run_rules(initial_facts: set[str], rules: list[dict]) -> dict:
    facts = set(initial_facts)
    fired = []
    fired_ids = set()
    changed = True
    while changed:
        changed = False
        for rule in rules:
            if rule["id"] in fired_ids:
                continue
            if set(rule["conditions"]).issubset(facts):
                fired_ids.add(rule["id"])
                if rule["conclusion"] not in facts:
                    facts.add(rule["conclusion"])
                    changed = True
                fired.append({
                    "id": rule["id"],
                    "title": rule["title"],
                    "explanation": rule["explanation"],
                    "conditions": rule["conditions"],
                    "conclusion": rule["conclusion"]
                })
    return {"facts": sorted(facts), "fired_rules": fired}
