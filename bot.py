import os
import pymongo
from telethon import TelegramClient, events

# MongoDB Configuration
MONGO_URL = os.environ.get("MONGO_URL") or "mongodb+srv://New_user_adi:radharani@atlascluster.tt1eq.mongodb.net/"
mongo_client = pymongo.MongoClient(MONGO_URL)
db = mongo_client["mangal_hardware"]
collection = db["categories"]

API_ID = int("23599783")
API_HASH ="62c4987db06716e25c4d68dcdcdc1ea5"
# Telethon Configuration
API_ID = os.environ.get("API_ID") or API_ID
API_HASH = os.environ.get("API_HASH") or API_HASH
BOT_TOKEN = "7728650601:AAHn1QxRambFq3yGsbuDAcYewXxHGjR-IdA"
# Initialize the Telethon client
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Global variable to hold user state
user_data = {}

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("Welcome! Use /add to add a category or /delete <index> to delete a category.")



@client.on(events.NewMessage())
async def receive_image(event):
    if event.chat_id in user_data and user_data[event.chat_id]["step"] == "image":
        user_data[event.chat_id]["image"] = event.message.message

        # Append the new category to the MongoDB collection
        new_category = {
            "name": user_data[event.chat_id]["name"],
            "image": user_data[event.chat_id]["image"],
            "products": []
        }

        # Update the database
        collection.update_one({}, {"$push": {"category": new_category}}, upsert=True)

        await event.respond(f"Category '{new_category['name']}' added successfully!")

        # Clean up user data
        del user_data[event.chat_id]

@client.on(events.NewMessage())
async def receive_name(event):
    if event.chat_id in user_data and user_data[event.chat_id]["step"] == "name":
        user_data[event.chat_id]["name"] = event.message.message
        await event.respond("Now send me the image URL.")
        user_data[event.chat_id]["step"] = "image"

@client.on(events.NewMessage(pattern='/add'))
async def add_category(event):
    await event.respond("Please send me the category name.")
    user_data[event.chat_id] = {"step": "name"}

@client.on(events.NewMessage(pattern='/delete_all'))
async def delete_all(event):
    # Update the document with _id: 0 to set its content to an empty object
    result = collection.update_one({"_id": 0}, {"$set": {"category": []}})

    if result.modified_count > 0:
        response_message = "All categories have been deleted successfully."
    else:
        response_message = "No categories found to delete or an error occurred."

    await event.respond(response_message)

@client.on(events.NewMessage(pattern='/delete'))
async def delete_category(event):
    try:
        index = int(event.message.message.split()[1])  # Get the index from the command
        # Find the current categories
        category_data = collection.find_one({}, {"_id": 0})

        if category_data and 0 <= index < len(category_data.get("category", [])):
            # Remove the specified category
            collection.update_one({}, {"$pull": {"category": {"name": category_data["category"][index]["name"]}}})
            await event.respond(f"Category '{category_data['category'][index]['name']}' deleted successfully!")
        else:
            await event.respond("Invalid index provided.")
    except (IndexError, ValueError):
        await event.respond("Please provide a valid index after /delete command.")


@client.on(events.NewMessage(pattern='/getdata'))
async def get_data(event):
    # Retrieve all categories from the MongoDB collection
    category_data = collection.find_one({}, {"_id": 0})
    event.respond(category_data)
    if category_data and "category" in category_data:
        categories = category_data["category"]
        if categories:
            response_message = "Current Categories:\n"
            for index, category in enumerate(categories):
                response_message += f"{index}: {category['name']} (Image URL: {category['image']})\n"
        else:
            response_message = "No categories found."
    else:
        response_message = "No categories found."

    await event.respond(response_message)

if __name__ == "__main__":
    client.run_until_disconnected()