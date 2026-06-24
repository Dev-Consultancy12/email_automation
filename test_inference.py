from services.enrichment import infer_name_from_email, infer_role_from_email

tests = [
    "john.smith@co.com",
    "sarah_jones@co.com",
    "sales@co.com",
    "info@co.com",
    "dpo@smallpdf.com",
    "privacy@smallpdf.com",
    "edgeone_developer@tencent.com",
    "policy@github.com",
    "esign@smallpdf.com",
]

print(f"{'Email':<45} {'Name':<25} Role")
print("-" * 90)
for e in tests:
    name = infer_name_from_email(e) or "Unknown"
    role = infer_role_from_email(e)
    print(f"{e:<45} {name:<25} {role}")
