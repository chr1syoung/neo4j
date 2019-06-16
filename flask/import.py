#!/usr/bin/python 

# -*- coding: utf-16 -*-
from py2neo import Node, Graph, Relationship ,NodeMatcher
from pandas import DataFrame
import pymysql
import os


class DataToNeo4j(object):
    """将excel中数据存入neo4j"""

    def __init__(self):
        """建立连接"""
        # link = Graph("http://localhost:7474", username="neo4j", password="neo4j")
        link = Graph(host='127.0.0.1', auth=('jzy', '19961105'))

        self.graph = link
        # 定义label
        self.lable_company = '公司名称'
        self.invoice_state = '当前状况'
        self.lable_executive = '高管名称'
        self.graph.delete_all()

    def create_node(self, company_list, executive_list):
        for i in range(0, len(company_list)):
            name_node = Node(self.lable_company, name = company_list[i][0], e_type = company_list[i][1], id = company_list[i][2])
            self.graph.create(name_node)
        for i in range(0, len(executive_list)):
            name_node = Node(self.lable_executive, name = executive_list[i])
            self.graph.create(name_node)        

# NodeMatcher(self.graph).match(self.invoice, name=df_data['name'][m]).first()
    def create_relation(self, df_data_1, df_data_2):
        for m in range(0, len(df_data_1)):
            try:
                # rel = Relationship(self.graph.find_one(label=self.invoice_name, property_key='name', property_value=df_data['name'][m]),
                # df_data['relation'][m], self.graph.find_one(label=self.invoice_name, property_key='name',property_value=df_data['name2'][m]))
                # self.graph.create(rel)
                rel = Relationship(NodeMatcher(self.graph).match(self.lable_company, name=df_data_1['name'][m]).first(),
                df_data_1['relation'][m], NodeMatcher(self.graph).match(self.lable_company, name=df_data_1['name2'][m]).first())
                rel['rate'] = df_data_1['rate'][m]
                self.graph.create(rel)
            except AttributeError as e:
                print(e, m)
        for m in range(0, len(df_data_2)):
            try:
                rel = Relationship(NodeMatcher(self.graph).match(self.lable_executive, name=df_data_2['name'][m]).first(),
                df_data_2['relation'][m], NodeMatcher(self.graph).match(self.lable_company, name=df_data_2['name2'][m]).first())
                self.graph.create(rel)
            except AttributeError as e:
                print(e, m)

def executive_extraction(invoice_data):
    executive_list = []
    for i in range(0, len(invoice_data)):
        executive_list.append(invoice_data[i][0])
    executive_list = list(set(executive_list))
    return executive_list

# def data_extraction(invoice_data):
#     """节点数据抽取"""

#     # 取出发票名称到list
#     node_list_key = []
#     for i in range(0, len(invoice_data)):
#         node_list_key.append(invoice_data[i][0])

#     # 去除重复的发票名称
#     node_list_key = list(set(node_list_key))
#     # value抽出作node
#     node_list_ISSUER = []
#     node_list_EXCHMARKET = []
#     node_list_RATING = []

#     for i in range(0, len(invoice_data)):
#             # 取出表头名称invoice_data.columns[i]
#         node_list_ISSUER.append(invoice_data[i][1])
#         if invoice_data[i][2] != None:
#             node_list_EXCHMARKET.append(invoice_data[i][2])
#         node_list_RATING.append(invoice_data[i][3])
#     # 去重
#     node_list_ISSUER = list(set(node_list_ISSUER))
#     node_list_EXCHMARKET = list(set(node_list_EXCHMARKET))
#     node_list_RATING = list(set(node_list_RATING))
#     # 将list中浮点及整数类型全部转成string类型
#     node_list_ISSUER = [str(i) for i in node_list_ISSUER]
#     node_list_EXCHMARKET = [str(i) for i in node_list_EXCHMARKET]
#     node_list_RATING = [str(i) for i in node_list_RATING]

#     return node_list_key, node_list_ISSUER, node_list_EXCHMARKET, node_list_RATING

def relation_extraction(investment_data, executive_data):
    links_dict = {}
    name_list = []
    relation_list = []
    name2_list = []
    rate_list = []
    for i in range(0, len(investment_data)):
        name_list.append(investment_data[i][0])
        relation_list.append('投资')
        name2_list.append(investment_data[i][1])
        rate_list.append(investment_data[i][2])
    # 整合数据，将三个list整合成一个dict
    links_dict['name'] = name_list
    links_dict['relation'] = relation_list
    links_dict['name2'] = name2_list
    links_dict['rate'] = rate_list
    # 将数据转成DataFrame
    df_investment_data = DataFrame(links_dict)

    links_dict = {}
    name_list = []
    relation_list = []
    name2_list = []
    for i in range(0, len(executive_data)):
        name_list.append(executive_data[i][0])
        relation_list.append(executive_data[i][1])
        name2_list.append(executive_data[i][2])
    # 整合数据，将三个list整合成一个dict
    links_dict['name'] = name_list
    links_dict['relation'] = relation_list
    links_dict['name2'] = name2_list
    # 将数据转成DataFrame
    df_executive_data = DataFrame(links_dict)    
    return df_investment_data, df_executive_data

# graph = Graph("http://localhost:7474", username="neo4j", password="19961105")

try:
    conn = pymysql.connect("localhost", "root", "19961105", "project")
    cursor = conn.cursor()
except Exception as e:
    print('Connect crawl_db error')
    exit()

sql = """SELECT `name`, `enterprise_type`, `c_id` FROM c_client_copy1 """#获取公司节点信息
try:
    conn.ping()
    cursor.execute(sql)
except Exception as e:
    print(e)
    exit()
company_list = cursor.fetchall()

sql = """SELECT `c_name`, `name`, `rate` FROM c_investment_copy1 """#获取公司投资信息
try:
    conn.ping()
    cursor.execute(sql)
except Exception as e:
    print(e)
    exit()
investment_data = cursor.fetchall()

sql = """SELECT `e_name`, `post`, `c_name` FROM client_executive_copy1 """#获取公司高管信息
try:
    conn.ping()
    cursor.execute(sql)
except Exception as e:
    print(e)
    exit()
executive_data = cursor.fetchall()

if company_list:
    executive_list = executive_extraction(executive_data)
    re1, re2 = relation_extraction(investment_data, executive_data)

    create_data = DataToNeo4j()
    create_data.create_node(company_list, executive_list)
    create_data.create_relation(re1, re2)
    # exit()
