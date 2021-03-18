
import jieba
import jieba.analyse
import csv
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import re

pd.options.display.max_columns = 30

TEXT_DATA = "all_data.csv"

NEW_STOP_WORDS = ['的', '和', '要', '在', '是', '了', '中国', '我们', '人民', '新', '为', '国家', '工作', '对', '等', '国际', '坚持', '世界', '合作', '加强', '推动', '中', '党', '有', '上', '把', '不', '社会', '全面', '问题', '将', '全球', '创新', '我国', '们', '以', '我', '实现', '年', '向', '更', '社会主义', '也',
                  '都', '推进', '群众', '组织', '各国', '同', '重要', '体系', '更加', '好', '支持', '重大', '历史', '大', '精神', '伟大', '时代', '人类', '到', '能力', '全国', '斗争', '就', '党中央', '制度', '最', '不断', '构建', '安全', '习近平', '领导', '必须', '国内', '共同', '年月日', '中华民族', '一个', '提高', '稳定', '作出', '教育', '方面']


def custom_tokenize(text):
    '''
    Removes numbers and punctuations.
    Uses 'accurate mode (cut_all=False)' when tokenizing chinese words.
    '''
    text_no_num = re.sub(r'[0-9]', '', text)
    text_no_punctuation = re.sub(r'[^\w]', '', text_no_num)

    return jieba.lcut(text_no_punctuation, cut_all=False)


def process_data(datafile=TEXT_DATA):
    '''
    Takes in csv containing raw data, and return a df grouping speeches by month
    '''
    df = pd.read_csv(TEXT_DATA)

    # convert to datetime object and extract month
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['Month'] = df['Date'].dt.month

    # combine speeches from the same month together
    df_month = df.groupby('Month')['Text'].apply(
        ','.join).str.replace("\u3000", "").reset_index()

    # display all content in column
    pd.set_option('display.max_colwidth', None)

    return df_month


def breakdown_by_month(datafile=TEXT_DATA):
    '''
    Return number of speeches made per month in tabular form.
    '''
    df = pd.read_csv(TEXT_DATA)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['Month'] = df['Date'].dt.month
    df_month = df.groupby('Month').count()

    return df_month.T


def get_most_common_terms(datafile=TEXT_DATA, n=100):
    '''
    To determine possible stop words.

    Code referenced: 
    https://medium.com/@cristhianboujon/how-to-list-the-most-common-words-from-text-corpus-using-scikit-learn-dad4d0cab41d
    '''
    df_month = process_data(datafile=TEXT_DATA)
    speech_by_month = [df_month.Text.loc[i] for i in range(0, 12)]

    # td-idf scores for terms
    count_vectorizer = CountVectorizer(tokenizer=custom_tokenize)
    X = count_vectorizer.fit_transform(speech_by_month)

    sum_words = X.sum(axis=0)
    words_freq = [(word, sum_words[0, idx])
                  for word, idx in count_vectorizer.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    words_freq_no_count = [word for word, _ in words_freq]

    return words_freq_no_count[: n]


def get_top_k_tokens(datafile=TEXT_DATA):
    '''
    Create a csv for each month, sorting terms by their TF-IDF scores.
    Code referenced: 
    https://programminghistorian.org/en/lessons/analyzing-documents-with-tfidf
    '''
    df_month = process_data(datafile=TEXT_DATA)
    speech_by_month = [df_month.Text.loc[i] for i in range(0, 12)]

    # term frequnecy within each documnet
    idf_vectorizer = TfidfVectorizer(
        stop_words=NEW_STOP_WORDS, tokenizer=custom_tokenize, use_idf=True)
    X = idf_vectorizer.fit_transform(speech_by_month)
    tf_df_all_months = pd.DataFrame(
        X.toarray(), columns=idf_vectorizer.get_feature_names())

    # for each month, we want a csv with term idf value
    tf_array_all_months = X.toarray()
    for month, month_data in enumerate(tf_array_all_months):
        file_name = "processed_data/" + "month" + str(month+1) + ".csv"
        # construct term, score tuples
        tf_idf_tuples = list(
            zip(idf_vectorizer.get_feature_names(), month_data))
        # create df for each month
        month_df = pd.DataFrame.from_records(tf_idf_tuples,
                                             columns=['term', 'score']).sort_values(by='score', ascending=False).reset_index(drop=True)

        # output to a csv
        month_df.to_csv(file_name)

    return tf_df_all_months
