# Researcher-only output (pre-Analyst) — Case_01_Southwest_Airlines_2022_Meltdown.md
Original run at: 2026-07-22T19:13:21
Archived because run_researcher_all_cases.py later overwrote the original
filename with the combined Researcher+Analyst output, using the same name.

To analyze the Southwest Airlines December 2022 operational meltdown, the following frameworks are essential for dissecting the systemic, multi-faceted failure:

### 1. Fishbone (Ishikawa) Diagram
*   **Definition:** A visual brainstorming tool that maps every plausible cause of a problem into major categories branching off a central spine leading to the problem “head,” resembling a fish skeleton. Also called a cause-and-effect diagram, it was developed by Kaoru Ishikawa in 1943 and popularized through Toyota’s quality circles in the 1960s.
*   **When to Use It:** Use when a problem likely has multiple, interacting causes across different areas (people, process, equipment, materials) rather than one obvious linear chain — for example, a persistent quality defect, a recurring customer-complaint pattern, or a process failure with no single clear explanation. It is often paired with 5 Whys to drill deeper into each branch once causes are mapped.
*   **Justification:** This case involves a complex interaction between external environmental factors (storm), internal processes (network structure), technology (crew-scheduling software), and management decisions (investment debt), making the Fishbone an ideal tool to categorize these varied contributors.

### 2. Root Cause Analysis (5 Whys)
*   **Definition:** A simple, iterative interrogative technique used to explore the cause-and-effect relationships underlying a particular problem. The primary goal is to determine the root cause of a defect or problem by repeating the question "Why?" (usually five times). Each answer forms the basis of the next question.
*   **When to Use It:** Best suited to a single, moderately complex problem with a fairly linear cause-and-effect chain — for example, a recurring operational failure, a missed deadline, or a quality defect. It works well as a quick, low-cost first pass before deploying heavier tools. For problems with many interacting causes across different areas, it is often paired with a Fishbone diagram rather than used alone.
*   **Justification:** While the overall crisis is systemic, the 5 Whys is the perfect technique to drill down into the "machine" and "method" branches of the Fishbone diagram—specifically, why the crew-scheduling software could not handle the scale of the disruption and why the organization ignored previous warnings from the pilot union.

### 3. Pareto Analysis (80/20 Rule)
*   **Definition:** A decision-making technique based on the Pareto Principle, which suggests that in many events, roughly 80% of the effects come from 20% of the causes. It involves identifying the "vital few" inputs or problems that are causing the majority of the negative (or positive) outcomes.
*   **When to Use It:** Use when you have a list of many possible problems or causes and need to prioritize where to focus resources for the greatest impact. It is most effective when you have quantitative data that can be ranked by frequency, cost, or impact.
*   **Justification:** The meltdown had many contributing factors (weather, staffing, network, tech). Pareto Analysis helps in quantifying which of these factors (e.g., the legacy tech vs. network structure) contributed the most to the massive $1.1B+ financial loss and the duration of the cancellation period, ensuring that the corrective investment (the $1.3B) is allocated to the most critical "vital few" drivers.
