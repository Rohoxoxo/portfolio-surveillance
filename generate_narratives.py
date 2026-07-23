import os
import pandas as pd
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

df = pd.read_csv("dashboard_export.csv")

flagged = df[df["Is Flagged"].astype(str).str.contains("Flagged", na=False)]

print(f"Found {len(flagged)} flagged manager-quarters")

narratives = []

for _, row in flagged.iterrows():
    prompt = f"""You are writing a short, factual note for a compliance analyst reviewing institutional investor risk.

Manager: {row['manager_name']}
Quarter: {row['year']} Q{row['quarter']}
Concentration (HHI): {row['HHI']:.3f} (peer-relative z-score: {row['HHI Z-Score']:.2f})
Turnover peer-relative z-score: {row['Turnover Z-Score']:.2f}
Tracking deviation vs benchmark, peer-relative z-score: {row['Tracking Deviation Z-Score']:.2f}
Composite Surveillance Score: {row['Composite Surveillance Score']:.2f}
Overall peer rank this quarter (1 = highest risk): {row['Surveillance Rank']}

Write exactly 2-3 sentences explaining, in plain factual language, why this manager was flagged this quarter. Reference the specific numbers above directly. Do not speculate about causes you cannot know from the data. Do not use hedging filler phrases. Do not include a title, header, or markdown formatting — output only the plain paragraph text."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    narrative_text = response.content[0].text.strip()

    narratives.append({
        "manager_name": row["manager_name"],
        "year": row["year"],
        "quarter": row["quarter"],
        "narrative": narrative_text,
    })

    print(f"\n{row['manager_name']} ({row['year']} Q{row['quarter']}):")
    print(narrative_text)

narrative_df = pd.DataFrame(narratives)
narrative_df.to_csv("fact_narrative.csv", index=False)
print(f"\nSaved {len(narrative_df)} narratives to fact_narrative.csv")
