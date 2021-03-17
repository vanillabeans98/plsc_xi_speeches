
from os import listdir
import pandas as pd
import numpy as np
import csv
import re
import matplotlib.pyplot as plt


# manually sort 30 terms by their respective categories
PROCESSED_DIR = "processed_data/"
SUMMARY_STATS = "summary_stat.csv"

CATEGORIES = {"economy": ("复工", "发展", "产业", "建设", "企业家", "投行", "企业",
                          "经济", "市场", "市场主体", "工商户", "基础设施", "循环",
                          "经济特区", "深圳", "改革", "开放", "劳动", "改革", "现代化",
                          "工人阶级", "开发", "生产", "收入", "资金"),
              "covid": ("疫情", "防控", "救治", "湖北", "患者", "应急", "公共卫生",
                        "武汉", "医疗", "疫情", "世卫", "抗疫", "生命", "新冠", "传染病",
                        "健康", "联防", "联控", "医务人员", "肺炎", "卫生", "抗疫",
                        "亚太经合组织"),
              "poverty": ("脱贫", "扶贫", "攻坚", "贫困人口", "贫困地区", "摘帽", "贫困",
                          "贫困县", "建档立卡", "减贫", "贫困村", "帮扶", "攻坚战",
                          "脱贫致富")}


def get_stats(processed_data=PROCESSED_DIR, n=30, summary_stats="summary_stat.csv"):
    '''
    Generate a summary statistics csv file
    '''

    with open(summary_stats, "w") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(
            ['month', 'economy_score', 'covid_score', 'poverty_score'])

        for speech_month in listdir(processed_data):
            economy_score = 0
            covid_score = 0
            poverty_score = 0
            df = pd.read_csv(PROCESSED_DIR+speech_month)

            for index, row in df.iterrows():
                if row['term'] in CATEGORIES['economy']:
                    economy_score += row['score']
                elif row['term'] in CATEGORIES['covid']:
                    covid_score += row['score']
                elif row['term'] in CATEGORIES['poverty']:
                    poverty_score += row['score']
                if index == n:
                    break

            row = [re.findall('\d+', speech_month)[0], economy_score,
                   covid_score, poverty_score]
            csvwriter.writerow(row)


def plotgraph(summary_stats=SUMMARY_STATS):
    '''
    '''
    # import data
    data = pd.read_csv(summary_stats)
    data = data.sort_values('month', ascending=True).set_index('month')

    fig = plt.figure()
    plt.plot(data['economy_score'], color="pink", label="Economy Score")
    # plt.plot(data['covid_score'], color="blue", label="COVID-19 Score")
    # plt.plot(data['poverty_score'], color="orange", label="Poverty Score")

    plt.title("Fig 3: Emphasis on Economic Development in 2020")
    plt.xlabel("Month")
    plt.ylabel("Total TF-IDF \nScore of   \nTop 30 Terms",
               rotation=0, ha="right")
    plt.legend()
    plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
                              'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.margins(0.025)
    fig.savefig('poverty.jpeg', format='jpeg', dpi=1200, bbox_inches="tight")
