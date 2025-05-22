import json
import os
from collections import deque

class User:
    def __init__(self, user_id, name, age, location, interests, friends):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.location = location
        self.interests = interests
        self.friends = friends

def load_users(filename):
    with open(filename, 'r') as f:
        raw_data = json.load(f)
    users = []
    for uid, info in raw_data.items():
        users.append(User(uid, info['name'], info['age'], info['location'], info['interests'], info['friends']))
    return users, raw_data

def add_user():
    filename = "data.json"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
    else:
        data = {}

    name = input("Enter name: ").strip()
    age = int(input("Enter age: "))
    location = input("Enter location: ").strip()
    interests = input("Enter interests (comma-separated): ").split(',')
    interests = [i.strip() for i in interests]

    new_user_id = f"u{len(data) + 1}"
    print("Existing users:", list(data.keys()))
    friends = input("Enter friend user IDs (comma-separated): ").split(',')
    friends = [f.strip() for f in friends if f.strip() in data]

    new_user = {
        "name": name,
        "age": age,
        "location": location,
        "interests": interests,
        "friends": friends
    }

    data[new_user_id] = new_user
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"New user '{name}' added as {new_user_id}!")

def suggest_mutual_friends(user_id, data):
    if user_id not in data:
        return []

    visited = set()
    queue = deque()
    suggestions = set()
    direct_friends = set(data[user_id]["friends"])

    queue.append((user_id, 0))
    visited.add(user_id)

    while queue:
        current_user, level = queue.popleft()
        if level > 2:
            continue

        for friend_id in data[current_user]["friends"]:
            if friend_id not in visited:
                queue.append((friend_id, level + 1))
                visited.add(friend_id)
                if level == 1 and friend_id != user_id and friend_id not in direct_friends:
                    suggestions.add(friend_id)
    return list(suggestions)

def jaccard_similarity(user_a, user_b):
    set_a = set(user_a.interests)
    set_b = set(user_b.interests)
    intersection = set_a & set_b
    union = set_a | set_b
    if not union:
        return 0.0, set()
    return len(intersection) / len(union), intersection

def count_mutual_friends(user_a, user_b):
    return len(set(user_a.friends) & set(user_b.friends))

def find_matches(user_id, users, raw_data):
    base_user = next((u for u in users if u.user_id == user_id), None)
    if not base_user:
        print("User not found.")
        return

    print(f"\nFriend Suggestions for {base_user.name} (Jaccard + Mutual + Location):\n")

    for user in users:
        if user.user_id == base_user.user_id or user.user_id in base_user.friends:
            continue

        similarity, match_interests = jaccard_similarity(base_user, user)
        mutuals = count_mutual_friends(base_user, user)
        same_loc = base_user.location == user.location

        if similarity >= 0.3 or mutuals >= 1 or same_loc:
            print(f"{user.name} ({user.user_id})")
            print(f"  - Matched Interests: {list(match_interests)}")
            print(f"  - Mutual Friends: {mutuals}")
            print(f"  - Same Location: {'Yes' if same_loc else 'No'}\n")

def main():
    print("\n--- FriendLink Menu ---")
    print("1. Add New User")
    print("2. Suggest Friends (Mutual + Jaccard)")
    choice = input("Enter choice (1/2): ").strip()

    filename = "data.json"

    if choice == '1':
        add_user()
    elif choice == '2':
        if not os.path.exists(filename):
            print("\nNo data available. Please add users first.")
            return
        users, raw_data = load_users(filename)
        user_id = input("Enter user ID (e.g., u1): ").strip()

        mutuals = suggest_mutual_friends(user_id, raw_data)
        if mutuals:
            print("\nMutual Friend Suggestions:")
            for uid in mutuals:
                print(f" - {uid} ({raw_data[uid]['name']})")
        else:
            print("\nNo mutual friends found.")

        find_matches(user_id, users, raw_data)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
