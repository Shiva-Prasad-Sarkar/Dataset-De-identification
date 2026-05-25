import pandas as pd
import numpy as np

np.random.seed(0)
n = 10

data = {
    "Timestamp": pd.date_range("2024-01-01", periods=n, freq="D").astype(str),
    "Email Address": [f"respondent{i}@example.com" for i in range(1, n + 1)],
    "What is your age group?": np.random.choice(["18-24","25-34","35-44","45+"], n),
    "What is your gender?": np.random.choice(["Male","Female","Non-binary","Prefer not to say"], n),
    "How satisfied are you with the service? (1-5)": np.random.randint(1, 6, n),
    "How likely are you to recommend us? (1-10)": np.random.randint(1, 11, n),
    "How often do you use the service?": np.random.choice(["Daily","Weekly","Monthly","Rarely"], n),
    "Which feature do you use most?": np.random.choice(["Search","Messaging","Dashboard","Reports"], n),
    "How easy is the interface to use? (1-5)": np.random.randint(1, 6, n),
    "Would you use this again?": np.random.choice(["Yes","No","Maybe"], n),
    "Rate our customer support (1-5)": np.random.randint(1, 6, n),
    "How did you hear about us?": np.random.choice(["Social media","Friend","Ad","Search engine"], n),
    "Do you use the mobile app?": np.random.choice(["Yes","No"], n),
    "Please share any additional comments:": [
        "Great service overall.", "Could improve speed.", "Loved the new update.",
        "Support was helpful.", "UI needs work.", "Very satisfied!",
        "Would love dark mode.", "Nothing to add.", "Keep it up!", "Needs more features."
    ],
}

df = pd.DataFrame(data)
df.to_csv("example/sample_survey.csv", index=False)
print(f"Sample CSV created: example/sample_survey.csv ({df.shape[0]} rows × {df.shape[1]} cols)")
