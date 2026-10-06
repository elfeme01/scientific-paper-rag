# Evaluation

Corpus: 2 papers (23 pages). Retrieval: top-k chunks, chunk size 1000, overlap 200.
Ground truth was written from the PDFs before running the system.

| # | Category | Question | Expected answer (page) | k=3 answer | k=3 sources | k=6 answer | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Out of scope | What is the impact of ocean temperature on whale migration patterns in the Pacific Ocean? | should refuse | | | | |
| 2 | Out of scope | What are the primary ingredients and baking techniques used in traditional Neapolitan pizza preparation? | should refuse | | | | |
| 3 | Both papers | Which AI/ML technology is used as the core for decision-making or detection in each of the two frameworks? | | | | | |
| 4 | Both papers / false premise? | Which popular cloud environment or execution tool is explicitly mentioned in both studies? | | | | | |
| 5 | Paper 1 | Which specific YOLO model (version) is integrated into the proposed framework? | | | | | |
| 6 | Paper 1 | How many annotated images from the Telegram app interface were in the custom dataset? | | | | | |
| 7 | Paper 1 | What is the task success rate of the proposed Intelligent RPA vs the traditional baseline? | | | | | |
| 8 | Paper 1 | Which tool was used to implement the traditional baseline RPA? | | | | | |
| 9 | Paper 1 | Which large-scale dataset was used for pretraining the detection model? | | | | | |
| 10 | Paper 2 | What was the duration of the empirical evaluation, and across how many organizations? | | | | | |
| 11 | Paper 2 | What are the five core components of the proposed ML-DevOps architecture? | | | | | |
| 12 | Paper 2 | Which RL algorithm and network architecture does the RL agent use? | | | | | |
| 13 | Paper 2 | Which open repositories were used to create the synthetic datasets? | | | | | |
| 14 | Greek (pair of 7) | Ποια είναι η τιμή του ποσοστού επιτυχίας εργασιών (Task success rate) που επιτυγχάνει το προτεινόμενο Intelligent RPA συγκριτικά με το παραδοσιακό baseline; | same as 7 | | | | |
| 15 | Greek (pair of 10) | Πόσος χρόνος διήρκεσε συνολικά η εμπειρική αξιολόγηση του ML-DevOps framework και σε πόσες οργανώσεις πραγματοποιήθηκε η δοκιμή; | same as 10 | | | | |