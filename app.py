import streamlit as st
from textblob import TextBlob
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Set the page configuration with a custom title
st.set_page_config(page_title="SoulScript", page_icon="📝")

# Display the app name at the top
st.title("SoulScript")

# Initialize prompts
prompts = [
    "Describe something that made you smile today.",
    "What’s been on your mind lately?",
    "If you could change one thing about your day, what would it be?",
    "What are three things you’re grateful for?",
    "Write about a challenge you overcame recently."
]

# Sentiment Analysis Function
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity  # Returns a value between -1 and 1
    return round((polarity + 1) * 5, 2)  # Normalize to a 0-10 scale

# Initialize CSV file
def init_csv():
    try:
        data = pd.read_csv("entries.csv")
    except FileNotFoundError:
        data = pd.DataFrame(columns=["Date", "Entry", "Mood"])
        data.to_csv("entries.csv", index=False)

# Main App
def main():
    st.subheader("Welcome to SoulScript: Your Journaling and Mood Tracker")

    # Sidebar for navigation
    menu = ["Journal Entry", "Mood Report"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Journal Entry":
        st.subheader("Write Your Journal")

        # Writing mode: Free writing or Prompt-based
        mode = st.radio("How would you like to start?", ["Write What's on My Mind", "Give Me a Prompt"])

        if mode == "Give Me a Prompt":
            prompt = st.selectbox("Choose a prompt:", prompts)
            st.write(f"Prompt: {prompt}")
        else:
            prompt = ""

        # Text input area
        journal_entry = st.text_area("Write your journal entry below:", placeholder="Start typing here...")

        # Submission button
        if st.button("Submit Entry"):
            if journal_entry.strip():
                # Analyze sentiment
                mood_score = analyze_sentiment(journal_entry)
                st.metric("Mood Score (out of 10)", mood_score)

                # Recommendations based on mood score
                if mood_score < 5:
                    st.warning("It seems you’re feeling low. Try reaching out to a friend or doing something uplifting!")
                else:
                    st.success("Great mood! Keep spreading positivity!")

                # Save entry to CSV
                date = datetime.now().strftime("%Y-%m-%d")
                new_entry = {"Date": date, "Entry": journal_entry, "Mood": mood_score}
                data = pd.read_csv("entries.csv")
                new_entry_df = pd.DataFrame([new_entry])  # Convert new entry to DataFrame
                data = pd.concat([data, new_entry_df], ignore_index=True)  # Concatenate
                data.to_csv("entries.csv", index=False)
            else:
                st.error("Please write something before submitting!")

    elif choice == "Mood Report":
        st.subheader("Your Mood Analysis for the Current Week")

        try:
            # Load data
            data = pd.read_csv("entries.csv")
            data["Date"] = pd.to_datetime(data["Date"])

            # Get the current week's start (Monday) and end (Sunday)
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())  # Monday
            end_of_week = start_of_week + timedelta(days=6)  # Sunday

            # Filter data for the current week
            current_week_data = data[(data["Date"] >= start_of_week) & (data["Date"] <= end_of_week)]

            if not current_week_data.empty:
                st.write("Here’s your mood trend for the current week (Monday to Sunday):")

                # Plot mood trends for the current week
                plt.figure(figsize=(10, 5))
                plt.plot(current_week_data["Date"], current_week_data["Mood"], marker="o", label="Mood Score")
                plt.xlabel("Date")
                plt.ylabel("Mood Score")
                plt.title("Mood Trend for the Current Week")
                plt.xticks(current_week_data["Date"], current_week_data["Date"].dt.strftime("%Y-%m-%d"), rotation=45)
                plt.legend()
                st.pyplot(plt)

                # Displaying the report for the current week
                if st.button("Generate Mood Report"):
                    st.write("### Text Report of Your Entries:")

                    # Loop through entries and print a summary
                    for _, row in current_week_data.iterrows():
                        st.write(f"**Date**: {row['Date'].strftime('%Y-%m-%d')}")
                        st.write(f"**Mood Score**: {row['Mood']}")
                        st.write(f"**Journal Entry**: {row['Entry']}")
                        st.write("\n")

                    # Average mood score for the current week
                    avg_mood = current_week_data["Mood"].mean()
                    st.write(f"### Average Mood Score for the Current Week: {round(avg_mood, 2)}")

                    # Mood interpretation
                    if avg_mood < 5:
                        st.warning("Your mood over the current week seems a bit low. Consider taking some time for self-care.")
                    else:
                        st.success("Your mood has been positive this week! Keep up the great work!")
            else:
                st.write("No entries found for the current week (Monday to Sunday). Start journaling to track your mood trends!")

        except FileNotFoundError:
            st.write("No data found. Start journaling to see your mood trends!")

# Run the app
if __name__ == "__main__":
    init_csv()
    main()
