# coding=utf-8
from flask import Flask,render_template
from py2neo import Node, Graph, Relationship ,NodeMatcher, RelationshipMatcher
from flask import Flask, jsonify, render_template, request
from pandas import DataFrame
import pymysql
import os
import sys
import numpy

app = Flask(__name__)

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

@app.route('/pic.html')
def to_pic():
    return render_template('pic.html')

@app.route('/tree-legend.html')
def to_tree():
    return render_template('tree-legend.html')

@app.route('/entrance.html')
def to_info():
    return render_template('entrance.html')

@app.route('/D3.html')
def to_D3():
    return render_template('D3.html')

@app.route('/D3test.html')
def to_D3test():
    return render_template('D3test.html')

@app.route('/D3test2.html')
def to_D3test2():
    return render_template('D3test2.html')

@app.route('/graph')
def get_graph():
    name = str(request.args.get('name'))
    graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
    nodes = list(map(buildNodes, graph.run("match (a:公司名称{name:\""+name+"\"})-[b]-(c:公司名称) return c.id, c.name, labels(c) as label")))
    nodes.append(buildNodes(graph.run("match (c:公司名称{name:\""+name+"\"}) return c.id, c.name, labels(c) as label").data()[0]))
    edges = list(map(buildEdges, graph.run("match (a:公司名称{name:\""+name+"\"})-[b]-(c:公司名称) return startnode(b).id as start,endnode(b).id as end,type(b) as type, b.rate as rate")))
    # nodes = list(map(buildNodes, graph.run("match (a:公司名称{name:'海航通航投资有限公司'})-[*1..2]-(c:公司名称) return c.id, c.name, labels(c) as label")))
    # nodes.append(buildNodes(graph.run("match (c:公司名称{name:'海航通航投资有限公司'}) return c.id, c.name, labels(c) as label").data()[0]))
    # edges = list(map(buildEdges, graph.run("match p = (a:公司名称{name:'海航通航投资有限公司'})-[*1..2]-(c:公司名称) where startnode(relationships(p)[1]).id is not null and endnode(relationships(p)[1]).id is not null return startnode(relationships(p)[1]).id as start,endnode(relationships(p)[1]).id as end ,type(relationships(p)[1]) as type, relationships(p)[1].rate as rate")))
    # edges2 = list(map(buildEdges, graph.run("match p = (a:公司名称{name:'海航通航投资有限公司'})-[*1..2]-(c:公司名称) where startnode(relationships(p)[1]).id is not null and endnode(relationships(p)[1]).id is not null return startnode(relationships(p)[0]).id as start,endnode(relationships(p)[0]).id as end ,type(relationships(p)[0]) as type, relationships(p)[0].rate as rate")))
    # edges.append(edges2)
    return jsonify(elements = {"nodes": nodes, "edges": edges})    

@app.route('/get_child')
def get_child():
	name = str(request.args.get('name'))    #http的get请求
	graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
	nodes = graph.run("match (a:公司名称{name:\""+name+"\"})-[:投资]->(c:公司名称) return c.name as name").data()   #查询数据信息
	return jsonify({"data": nodes})

@app.route('/get_father')
def get_father():
	name = str(request.args.get('name'))
	graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
	nodes = graph.run("match (a:公司名称{name:\""+name+"\"})<-[:投资]-(c:公司名称) return c.name as name").data()
	return jsonify({"data": nodes})

@app.route('/get_links')
def get_links():
        name = str(request.args.get('name'))
        graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
        links = graph.run("match (a:公司名称{name:\""+name+"\"})-[b]-(c) return startnode(b).name as source,endnode(b).name as target,type(b) as rela").data()
        return jsonify({"data": links})

@app.route('/get_D3')
def get_D3():
        name = str(request.args.get('name'))
        graph = Graph(host='127.0.0.1', auth=('jzy', '19961105'))
        # nodes = graph.run("match (a:公司名称{name:\""+name+"\"})-[*1..2]-(c) return id(c) as id, c.name as name, labels(c) as label").data()
        # nodes.append(graph.run("match (c:公司名称{name:\""+name+"\"}) return id(c) as id, c.name as name, labels(c) as label").data()[0])
        # edges = graph.run("match (a:公司名称{name:\""+name+"\"})-[b]-(c) return id(startnode(b)) as source,id(endnode(b)) as target,type(b) as rela").data()

        nodes = graph.run("match (a:公司名称{name:\""+name+"\"})-[*1..2]-(c) return id(c) as id, c.name as name, labels(c) as label").data()
        nodes.append(graph.run("match (c:公司名称{name:\""+name+"\"}) return id(c) as id, c.name as name, labels(c) as label").data()[0])
        edges = graph.run("match p = (a:公司名称{name:\""+name+"\"})-[*1..2]-(c) where id(startnode(relationships(p)[1])) is not null return id(startnode(relationships(p)[1])) as source, id(endnode(relationships(p)[1])) as target ,type(relationships(p)[1]) as rela").data()
        edges.extend(graph.run("match p = (a:公司名称{name:\""+name+"\"})-[*1..2]-(c) where id(startnode(relationships(p)[0])) is not null return id(startnode(relationships(p)[0])) as source, id(endnode(relationships(p)[0])) as target ,type(relationships(p)[0]) as rela").data())
        return jsonify(nodes, edges)
        # print (links)
if __name__ == '__main__':
    app.run(debug = True)    