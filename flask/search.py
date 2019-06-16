#!/usr/bin/python 

# -*- coding: utf-16 -*-
from py2neo import Node, Graph, Relationship ,NodeMatcher, RelationshipMatcher
from flask import Flask, jsonify, render_template
from pandas import DataFrame
import pymysql
import os
import sys
import numpy
import math
def search_node_name(node_name):# 根据节点名称寻找节点
    graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
    a = graph.run("match (a:公司名称{name:" + node_name + "}) return a").to_data_frame()
    # a = graph.nodes.match("公司名称", name=node_name).first()
    print (a)

def find_node_from(start_node, rel):#根据起始节点及关系名寻找目标节点
    graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
    a = graph.run("match (:公司名称{name:"+ start_node +"})-[:"+ rel +"]->(c:公司名称) return c").to_data_frame()
    print (a)

def find_node_to(end_node, rel):#根据目标节点及关系名寻找起始节点
    graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
    a = graph.run("match (:公司名称{name:"+ end_node +"})<-[:"+ rel +"]-(c:公司名称) return c").to_data_frame()
    print (a)

def search_node_property(property_name):# 根据e_type寻找节点信息
    graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
    a = graph.run("match (a:公司名称{e_type:" + property_name + "}) return a").to_data_frame()
    print(a)
    # matcher = NodeMatcher(graph)
    # node_list = list(matcher.match("公司名称", e_type=property_name))
    # for i in node_list:
    #     print (i)

def search_rel_name(rel_name):# 根据关系名寻找节点信息
    graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
    relMatch = RelationshipMatcher(graph)
    relList = list(relMatch.match(r_type=rel_name))
    for i in relList:
        print(i)

def find_rel_from_nodes(start_node, end_node):#根据起始以及结束节点查找关系类型
    graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
    a = graph.run("match (:公司名称{name:"+ start_node +"})-[a]->(:公司名称{name:"+ end_node +"}) return type(a)").to_data_frame()
    print (a)

def alter_node(node_name, new_name, new_type):#未测试
    graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
    a = graph.nodes.match("公司名称", name=node_name).first()
    if a:
        data = {}
        if new_name:
            data['name'] = new_name
        if new_type:
            data['e_type'] = new_type
        a.update(data)
        print(a)

def set_new_rel(node_a, node_b, rel_type):# 在已有节点间创建新的关系
    graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
    a = graph.nodes.match("公司名称", name=node_a).first()
    b = graph.nodes.match("公司名称", name=node_b).first()
    rel = Relationship(a, rel_type, b)
    graph.create(rel)

def delete_rel(node_a, node_b):# 删除特定关系
    graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
    graph.run("match (a:公司名称{name:"+ node_a +"}) -[b:测试关系]-> (c:公司名称{name:"+ node_b +"}) delete b")

def if_connected(node_a, node_b):#未测试
    graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
    result = graph.run("match (a:公司名称{name:" + node_a + "})-[*]->(b:公司名称{name:"+ node_b +"}) return a,b")
    print (result)

def test():
    graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
    a = graph.run("MATCH (a:公司名称) RETURN a.id, a.name").data()
    # list =[]
    # while a.forward():
    #     list.append(a.current)
    # print(list)
    for i in a:
        print(i)


#####
def buildNodes(nodeRecord):
    data = {"id": nodeRecord['c.id'], "name": nodeRecord['c.name'], "label":nodeRecord['label'][0]}
    return {"data": data}

def buildEdges(relationRecord):
    if relationRecord['start'] and relationRecord['end']:
        if numpy.isnan(relationRecord['rate']): 
                data = {"source": str(relationRecord['start']), 
                    "target": str(relationRecord['end']),
                    "relationship": relationRecord['type'],
                    "rate": "0"
                    }
        else:
                data = {"source": str(relationRecord['start']), 
                    "target": str(relationRecord['end']),
                    "relationship": relationRecord['type'],
                    "rate": relationRecord['rate']
                    }
        return {"data": data}

def buildEdges_for_D3(relationRecord):
    if relationRecord['start'] and relationRecord['end']:
        if numpy.isnan(relationRecord['rate']): 
                data = {"source": str(relationRecord['start']), 
                    "target": str(relationRecord['end']),
                    "rela": relationRecord['type'],
                    "rate": "0"
                    }
        else:
                data = {"source": str(relationRecord['start']), 
                    "target": str(relationRecord['end']),
                    "rela": relationRecord['type'],
                    "rate": relationRecord['rate']
                    }
        return {data}
def get_graph():
    graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
    nodes = list(map(buildNodes, graph.run("match (a:公司名称{name:'海航集团有限公司'})-[b]-(c:公司名称) return c.id, c.name, labels(c) as label")))
    nodes.append(buildNodes(graph.run("match (c:公司名称{name:'海航集团有限公司'}) return c.id, c.name, labels(c) as label").data()[0]))
    edges = list(map(buildEdges, graph.run("match (a:公司名称{name:'海航集团有限公司'})-[b]-(c:公司名称) return startnode(b).id as start,endnode(b).id as end,type(b) as type, b.rate as rate")))
#     nodes = list(map(buildNodes, graph.run("match (a:公司名称{name:'海航通航投资有限公司'})-[*1..2]-(c:公司名称) return c.id, c.name, labels(c) as label")))
#     nodes.append(buildNodes(graph.run("match (c:公司名称{name:'海航通航投资有限公司'}) return c.id, c.name, labels(c) as label").data()[0]))
#     edges = list(map(buildEdges, graph.run("match p = (a:公司名称{name:'海航通航投资有限公司'})-[*1..2]-(c:公司名称) where startnode(relationships(p)[1]).id is not null and endnode(relationships(p)[1]).id is not null return startnode(relationships(p)[1]).id as start,endnode(relationships(p)[1]).id as end ,type(relationships(p)[1]) as type, relationships(p)[1].rate as rate")))
#     edges2 = list(map(buildEdges, graph.run("match p = (a:公司名称{name:'海航通航投资有限公司'})-[*1..2]-(c:公司名称) where startnode(relationships(p)[1]).id is not null and endnode(relationships(p)[1]).id is not null return startnode(relationships(p)[0]).id as start,endnode(relationships(p)[0]).id as end ,type(relationships(p)[0]) as type, relationships(p)[0].rate as rate")))
#     edges.append(edges2)
    print({"nodes":nodes, "edges":edges})
#     edges = map(buildEdges, graph.cypher.execute('MATCH ()-[r]->() RETURN r'))  
#     return jsonify(elements = {"nodes": nodes}) 
def get_child():
	graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
	nodes = graph.run("match (a:公司名称{name:'海航集团有限公司'})-[:投资]->(c:公司名称) return c.name as name").data()
	print (nodes)

def get_father():
	graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
	nodes = graph.run("match (a:公司名称{name:'海航集团有限公司'})<-[:投资]-(c:公司名称) return c.name as name").data()
	print (nodes)

def get_links():
        # name = str(request.args.get('name'))
        name = "海航集团有限公司"
        graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
        nodes = graph.run("match (a:公司名称{name:\""+name+"\"})-[*1..2]-(c) return id(c) as id, c.name as name, labels(c) as label").data()
        nodes.append(graph.run("match (c:公司名称{name:\""+name+"\"}) return id(c) as id, c.name as name, labels(c) as label").data()[0])
        edges = graph.run("match p = (a:公司名称{name:\""+name+"\"})-[*1..2]-(c) return id(startnode(relationships(p)[1])) as source, id(endnode(relationships(p)[1])) as target ,type(relationships(p)[1]) as rela").data()
        edges.append(graph.run("match p = (a:公司名称{name:\""+name+"\"})-[*1..2]-(c) return id(startnode(relationships(p)[0])) as source, id(endnode(relationships(p)[0])) as target ,type(relationships(p)[0]) as rela").data())
        print (nodes)
        print (edges)
get_links()
# get_father()
# get_graph()
# search_node_name("'海航创新金融有限公司'")
# search_node_property("'其他有限责任公司'")
# search_rel_name("投资")
# alter_node("海航创新金融有限公司", '', '测试类型')
# set_new_rel('海航集团有限公司', '天津渤海现代物流有限责任公司', '测试关系')
# if_connected("'海航机场集团有限公司'", "'嘉兴领裕股权投资合伙企业(有限合伙)'")
# delete_rel("'海南海航航空进出口有限公司'", "'嘉兴领裕股权投资合伙企业(有限合伙)'")
# find_node_from("'海航创新金融有限公司'", '投资')
# find_rel_from_nodes("'海航创新金融有限公司'", "'海航丝路有限公司'")
# test()