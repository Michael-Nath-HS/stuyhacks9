from getpass import getpass

print("📋 Press 'S' to sign-up to SecurEvent")
print("🔑 Press 'L' to login to SecurEvent")
print("✏️ Press 'C' to create a SecurEvent")
print("🔍 Press 'V' to view a SecurEvent with its ID")
print("✉️ Press 'I' to invite someone to your SecurEvent")
print("👍 Press 'R' to respond to an invite to a SecurEvent")
response = input().lower()
if response == "s":
    user = input("Username: ")
    pw = getpass()
    print(pw)