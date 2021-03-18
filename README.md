# plsc_xi_speeches

This respository contains code and data used for the analysis of Xi Jinping's speeches in 2020.

# Files

plsc_crawler.py: Retrieves speeches uploaded to http://jhsjk.people.cn/ 

plsc_analyze.py: Aggregates speeches by month, tokenize into terms and calculate TF-IDF values for each term

trends.py: Categorizes terms by domains, plots graphs using the TF-IDF values

# Data

all_data.csv: CSV file containing all speeches retrieved

summary_stat.csv: CSV file containing the domain scores for each month

processed_data: Directory containing CSV files corresponding to each month, each file contains all tokenized terms and its associated TF-IDF value

